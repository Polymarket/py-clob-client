"""
Polymarket Directional Trading Bot

Entry point that starts:
1. The FastAPI HTTP server for control
2. The trading loop in a background thread

Environment Variables Required:
- POLY_PRIVATE_KEY: Your wallet private key
- POLY_API_KEY: Polymarket API key
- POLY_API_SECRET: Polymarket API secret
- POLY_API_PASSPHRASE: Polymarket API passphrase
- BOT_TOKEN: Secret token for API authentication

Optional:
- PORT: HTTP server port (default: 8000)
- POLY_HOST: CLOB host (default: https://clob.polymarket.com)
- LOOP_INTERVAL: Trading loop interval in seconds (default: 60)
"""

import asyncio
import logging
import os
import secrets
import threading
import time
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from bot.state import state
from bot.execution import engine
from bot.strategy import generate_signal, validate_signal, get_market_summary

# =============================================================================
# LOGGING
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

PORT = int(os.environ.get("PORT", 8000))
BOT_TOKEN = os.environ.get("BOT_TOKEN")
LOOP_INTERVAL = int(os.environ.get("LOOP_INTERVAL", 60))

# =============================================================================
# AUTHENTICATION
# =============================================================================

security = HTTPBearer()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Verify the Bearer token matches BOT_TOKEN."""
    if not BOT_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="BOT_TOKEN not configured on server",
        )

    if not secrets.compare_digest(credentials.credentials, BOT_TOKEN):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
        )

    return credentials.credentials


# =============================================================================
# TRADING LOOP
# =============================================================================

_loop_running = False
_loop_thread: Optional[threading.Thread] = None


def trading_loop():
    """
    Main trading loop that runs in a background thread.

    - Checks if paused, if so sleeps
    - Generates signals via strategy
    - Executes trades based on mode (paper/live)
    """
    global _loop_running
    _loop_running = True

    logger.info(f"Trading loop started (interval: {LOOP_INTERVAL}s)")

    while _loop_running:
        try:
            # Check if paused
            if state.paused:
                logger.debug("Bot is paused, sleeping...")
                time.sleep(LOOP_INTERVAL)
                continue

            # Generate trading signal
            signal = generate_signal()

            if signal is None:
                logger.debug("No signal generated")
                time.sleep(LOOP_INTERVAL)
                continue

            # Validate signal
            if not validate_signal(signal):
                logger.info(f"Signal failed validation: {signal}")
                time.sleep(LOOP_INTERVAL)
                continue

            logger.info(
                f"Signal: {signal.side} {signal.size} @ {signal.price:.4f} "
                f"({signal.reason}, confidence={signal.confidence:.2f})"
            )

            # Execute based on mode
            if state.mode == "paper":
                # Paper trading: log but don't execute
                logger.info(f"[PAPER] Would execute: {signal}")
                result = engine.place_order(
                    token_id=signal.token_id,
                    side=signal.side,
                    price=signal.price,
                    size=signal.size,
                    dry_run=True,
                )
            else:
                # Live trading: actually execute
                logger.info(f"[LIVE] Executing: {signal}")
                result = engine.place_order(
                    token_id=signal.token_id,
                    side=signal.side,
                    price=signal.price,
                    size=signal.size,
                    dry_run=False,
                )

            if result.success:
                logger.info(f"Trade result: SUCCESS - {result.details}")
            else:
                logger.warning(f"Trade result: FAILED - {result.error}")

        except Exception as e:
            logger.exception(f"Error in trading loop: {e}")

        time.sleep(LOOP_INTERVAL)

    logger.info("Trading loop stopped")


def start_trading_loop():
    """Start the trading loop in a background thread."""
    global _loop_thread
    if _loop_thread is not None and _loop_thread.is_alive():
        logger.warning("Trading loop already running")
        return

    _loop_thread = threading.Thread(target=trading_loop, daemon=True)
    _loop_thread.start()
    logger.info("Trading loop thread started")


def stop_trading_loop():
    """Stop the trading loop."""
    global _loop_running
    _loop_running = False
    logger.info("Trading loop stop requested")


# =============================================================================
# FASTAPI APP
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("Starting Polymarket Trading Bot...")

    # Initialize execution engine
    if engine.initialize():
        logger.info("Execution engine initialized")
    else:
        logger.warning("Execution engine failed to initialize (check env vars)")

    # Start trading loop
    start_trading_loop()

    yield

    # Shutdown
    logger.info("Shutting down...")
    stop_trading_loop()


app = FastAPI(
    title="Polymarket Trading Bot",
    description="Directional trading bot with HTTP control API",
    version="1.0.0",
    lifespan=lifespan,
)


# =============================================================================
# API MODELS
# =============================================================================

class RiskLimitsRequest(BaseModel):
    max_order_size: Optional[float] = None
    max_exposure_per_market: Optional[float] = None


class MessageResponse(BaseModel):
    message: str


# =============================================================================
# PUBLIC ENDPOINTS
# =============================================================================

@app.get("/health")
async def health():
    """Health check endpoint (no auth required)."""
    return {"status": "ok"}


# =============================================================================
# PROTECTED ENDPOINTS
# =============================================================================

@app.get("/status", dependencies=[Depends(verify_token)])
async def get_status():
    """Get current bot status."""
    status_data = state.get_status()
    status_data["engine_initialized"] = engine.is_initialized()

    # Add balance if available
    balance = engine.get_collateral_balance()
    if balance is not None:
        status_data["usdc_balance"] = balance

    return status_data


@app.post("/pause", dependencies=[Depends(verify_token)])
async def pause_bot():
    """Pause the trading bot."""
    state.set_paused(True)
    logger.info("Bot paused via API")
    return {"message": "Bot paused", "paused": True}


@app.post("/resume", dependencies=[Depends(verify_token)])
async def resume_bot():
    """Resume the trading bot."""
    state.set_paused(False)
    logger.info("Bot resumed via API")
    return {"message": "Bot resumed", "paused": False}


@app.post("/mode/{mode}", dependencies=[Depends(verify_token)])
async def set_mode(mode: str):
    """Set trading mode (paper or live)."""
    if mode not in ("paper", "live"):
        raise HTTPException(
            status_code=400,
            detail="Mode must be 'paper' or 'live'",
        )

    state.set_mode(mode)
    logger.info(f"Mode set to {mode} via API")
    return {"message": f"Mode set to {mode}", "mode": mode}


@app.post("/risk", dependencies=[Depends(verify_token)])
async def set_risk_limits(limits: RiskLimitsRequest):
    """Update risk limits."""
    state.set_risk_limits(
        max_order_size=limits.max_order_size,
        max_exposure_per_market=limits.max_exposure_per_market,
    )
    logger.info(f"Risk limits updated: {limits}")
    return {
        "message": "Risk limits updated",
        "risk_limits": {
            "max_order_size": state.risk_limits.max_order_size,
            "max_exposure_per_market": state.risk_limits.max_exposure_per_market,
        },
    }


@app.get("/markets", dependencies=[Depends(verify_token)])
async def get_markets():
    """Get summary of watched markets."""
    return get_market_summary()


@app.post("/cancel-all", dependencies=[Depends(verify_token)])
async def cancel_all_orders():
    """Cancel all open orders."""
    if state.mode == "paper":
        return {"message": "Paper mode: no orders to cancel"}

    result = engine.cancel_all_orders()
    if result.success:
        logger.info("All orders cancelled via API")
        return {"message": "All orders cancelled", "details": result.details}
    else:
        raise HTTPException(status_code=500, detail=result.error)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point."""
    # Validate required environment variables
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable is required")
        logger.error("Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
        exit(1)

    logger.info(f"Starting HTTP server on port {PORT}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info",
    )


if __name__ == "__main__":
    main()
