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
from fastapi.responses import HTMLResponse
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
# WEB UI
# =============================================================================

UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Trading Bot Control</title>
    <style>
        /* Reset and base styles */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            min-height: 100vh;
            padding: 16px;
            font-size: 16px;
            line-height: 1.5;
        }

        /* Container */
        .container {
            max-width: 480px;
            margin: 0 auto;
        }

        /* Header */
        h1 {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 16px;
            color: #fff;
        }

        h2 {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 12px;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Cards */
        .card {
            background: #16213e;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
        }

        /* Auth section */
        #auth-section {
            text-align: center;
            padding: 40px 20px;
        }

        #auth-section input {
            width: 100%;
            padding: 14px;
            font-size: 16px;
            border: 2px solid #333;
            border-radius: 8px;
            background: #0f0f23;
            color: #fff;
            margin-bottom: 12px;
        }

        #auth-section input:focus {
            outline: none;
            border-color: #4a9eff;
        }

        /* Status grid */
        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        .status-item {
            background: #0f0f23;
            padding: 12px;
            border-radius: 8px;
        }

        .status-item.full-width {
            grid-column: 1 / -1;
        }

        .status-label {
            font-size: 0.75rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }

        .status-value {
            font-size: 1.1rem;
            font-weight: 600;
            word-break: break-word;
        }

        /* Status badges */
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .badge-green {
            background: #0d4429;
            color: #3fb950;
        }

        .badge-red {
            background: #4a1515;
            color: #f85149;
        }

        .badge-yellow {
            background: #3d2e00;
            color: #d29922;
        }

        .badge-blue {
            background: #0d3049;
            color: #58a6ff;
        }

        /* Buttons */
        .btn-row {
            display: flex;
            gap: 10px;
            margin-bottom: 12px;
        }

        .btn {
            flex: 1;
            padding: 14px 16px;
            font-size: 1rem;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: opacity 0.2s, transform 0.1s;
        }

        .btn:active {
            transform: scale(0.98);
        }

        .btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
            transform: none;
        }

        .btn-primary {
            background: #238636;
            color: #fff;
        }

        .btn-danger {
            background: #da3633;
            color: #fff;
        }

        .btn-warning {
            background: #9e6a03;
            color: #fff;
        }

        .btn-secondary {
            background: #333;
            color: #fff;
        }

        /* Risk inputs */
        .input-group {
            margin-bottom: 12px;
        }

        .input-group label {
            display: block;
            font-size: 0.85rem;
            color: #888;
            margin-bottom: 6px;
        }

        .input-group input {
            width: 100%;
            padding: 12px;
            font-size: 16px;
            border: 2px solid #333;
            border-radius: 8px;
            background: #0f0f23;
            color: #fff;
        }

        .input-group input:focus {
            outline: none;
            border-color: #4a9eff;
        }

        /* Error/success messages */
        .message {
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 16px;
            font-size: 0.9rem;
        }

        .message-error {
            background: #4a1515;
            color: #f85149;
            border: 1px solid #f85149;
        }

        .message-success {
            background: #0d4429;
            color: #3fb950;
            border: 1px solid #3fb950;
        }

        /* Loading spinner */
        .loading {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #333;
            border-top-color: #fff;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-right: 8px;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Footer */
        .footer {
            text-align: center;
            color: #444;
            font-size: 0.8rem;
            margin-top: 24px;
        }

        /* Hide sections */
        .hidden {
            display: none !important;
        }

        /* Refresh indicator */
        .refresh-indicator {
            font-size: 0.75rem;
            color: #444;
            text-align: right;
            margin-bottom: 8px;
        }

        /* Logout link */
        .logout-link {
            color: #666;
            font-size: 0.85rem;
            text-decoration: none;
            cursor: pointer;
        }

        .logout-link:hover {
            color: #f85149;
        }

        .header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Auth Section (shown when no token) -->
        <div id="auth-section" class="card">
            <h1>Trading Bot</h1>
            <p style="color: #888; margin-bottom: 20px;">Enter your BOT_TOKEN to continue</p>
            <input type="password" id="token-input" placeholder="BOT_TOKEN" autocomplete="off">
            <button class="btn btn-primary" style="width: 100%;" onclick="authenticate()">Connect</button>
            <div id="auth-error" class="message message-error hidden" style="margin-top: 12px;"></div>
        </div>

        <!-- Main Section (shown when authenticated) -->
        <div id="main-section" class="hidden">
            <div class="header-row">
                <h1>Trading Bot</h1>
                <a class="logout-link" onclick="logout()">Logout</a>
            </div>

            <!-- Message area -->
            <div id="message" class="message hidden"></div>

            <!-- Status Panel -->
            <div class="card">
                <div class="refresh-indicator">
                    <span id="refresh-status">Auto-refresh: 5s</span>
                </div>
                <div class="status-grid">
                    <div class="status-item">
                        <div class="status-label">Status</div>
                        <div class="status-value" id="status-paused">--</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">Mode</div>
                        <div class="status-value" id="status-mode">--</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">Uptime</div>
                        <div class="status-value" id="status-uptime">--</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">Balance</div>
                        <div class="status-value" id="status-balance">--</div>
                    </div>
                    <div class="status-item full-width">
                        <div class="status-label">Last Command</div>
                        <div class="status-value" id="status-last-cmd">--</div>
                    </div>
                    <div class="status-item full-width">
                        <div class="status-label">Last Trade</div>
                        <div class="status-value" id="status-last-trade">--</div>
                    </div>
                </div>
            </div>

            <!-- Controls -->
            <div class="card">
                <h2>Controls</h2>
                <div class="btn-row">
                    <button id="btn-pause" class="btn btn-danger" onclick="pauseBot()">Pause</button>
                    <button id="btn-resume" class="btn btn-primary" onclick="resumeBot()">Resume</button>
                </div>
                <div class="btn-row">
                    <button id="btn-paper" class="btn btn-secondary" onclick="setMode('paper')">Paper Mode</button>
                    <button id="btn-live" class="btn btn-warning" onclick="setMode('live')">Live Mode</button>
                </div>
            </div>

            <!-- Risk Settings -->
            <div class="card">
                <h2>Risk Limits</h2>
                <div class="input-group">
                    <label>Max Order Size ($)</label>
                    <input type="number" id="input-max-order" placeholder="100" step="10" min="0">
                </div>
                <div class="input-group">
                    <label>Max Exposure Per Market ($)</label>
                    <input type="number" id="input-max-exposure" placeholder="500" step="50" min="0">
                </div>
                <button class="btn btn-secondary" style="width: 100%;" onclick="updateRisk()">Update Risk Limits</button>
            </div>

            <!-- Emergency -->
            <div class="card">
                <h2>Emergency</h2>
                <button class="btn btn-danger" style="width: 100%;" onclick="cancelAll()">Cancel All Orders</button>
            </div>

            <div class="footer">
                Polymarket Trading Bot
            </div>
        </div>
    </div>

    <script>
        // =================================================================
        // State
        // =================================================================
        let token = localStorage.getItem('bot_token') || '';
        let refreshInterval = null;
        let currentStatus = {};

        // =================================================================
        // Initialization
        // =================================================================
        function init() {
            if (token) {
                // Try to verify token by fetching status
                fetchStatus().then(valid => {
                    if (valid) {
                        showMain();
                        startAutoRefresh();
                    } else {
                        showAuth();
                    }
                });
            } else {
                showAuth();
            }
        }

        function showAuth() {
            document.getElementById('auth-section').classList.remove('hidden');
            document.getElementById('main-section').classList.add('hidden');
            stopAutoRefresh();
        }

        function showMain() {
            document.getElementById('auth-section').classList.add('hidden');
            document.getElementById('main-section').classList.remove('hidden');
        }

        // =================================================================
        // Authentication
        // =================================================================
        async function authenticate() {
            const input = document.getElementById('token-input');
            const errorDiv = document.getElementById('auth-error');
            const testToken = input.value.trim();

            if (!testToken) {
                showAuthError('Please enter a token');
                return;
            }

            // Test the token
            try {
                const response = await fetch('/status', {
                    headers: { 'Authorization': 'Bearer ' + testToken }
                });

                if (response.ok) {
                    token = testToken;
                    localStorage.setItem('bot_token', token);
                    errorDiv.classList.add('hidden');
                    showMain();
                    startAutoRefresh();
                } else if (response.status === 401) {
                    showAuthError('Invalid token');
                } else {
                    showAuthError('Server error: ' + response.status);
                }
            } catch (e) {
                showAuthError('Connection failed');
            }
        }

        function showAuthError(msg) {
            const errorDiv = document.getElementById('auth-error');
            errorDiv.textContent = msg;
            errorDiv.classList.remove('hidden');
        }

        function logout() {
            token = '';
            localStorage.removeItem('bot_token');
            showAuth();
        }

        // =================================================================
        // API Calls
        // =================================================================
        async function apiCall(method, endpoint, body = null) {
            const options = {
                method: method,
                headers: {
                    'Authorization': 'Bearer ' + token
                }
            };

            if (body) {
                options.headers['Content-Type'] = 'application/json';
                options.body = JSON.stringify(body);
            }

            const response = await fetch(endpoint, options);

            if (response.status === 401) {
                logout();
                throw new Error('Authentication failed');
            }

            if (!response.ok) {
                const data = await response.json().catch(() => ({}));
                throw new Error(data.detail || 'Request failed');
            }

            return response.json();
        }

        // =================================================================
        // Status
        // =================================================================
        async function fetchStatus() {
            try {
                const data = await apiCall('GET', '/status');
                currentStatus = data;
                updateStatusUI(data);
                return true;
            } catch (e) {
                if (e.message === 'Authentication failed') {
                    return false;
                }
                console.error('Status fetch error:', e);
                return true; // Don't logout on network errors
            }
        }

        function updateStatusUI(data) {
            // Paused status
            const pausedEl = document.getElementById('status-paused');
            if (data.paused) {
                pausedEl.innerHTML = '<span class="badge badge-red">PAUSED</span>';
            } else {
                pausedEl.innerHTML = '<span class="badge badge-green">RUNNING</span>';
            }

            // Mode
            const modeEl = document.getElementById('status-mode');
            if (data.mode === 'live') {
                modeEl.innerHTML = '<span class="badge badge-yellow">LIVE</span>';
            } else {
                modeEl.innerHTML = '<span class="badge badge-blue">PAPER</span>';
            }

            // Uptime
            document.getElementById('status-uptime').textContent = data.uptime_human || '--';

            // Balance
            const balance = data.usdc_balance;
            document.getElementById('status-balance').textContent =
                balance !== undefined ? '$' + balance.toFixed(2) : '--';

            // Last command
            const lastCmd = data.last_command;
            const lastCmdTime = data.last_command_time;
            if (lastCmd) {
                const time = lastCmdTime ? formatTime(lastCmdTime) : '';
                document.getElementById('status-last-cmd').textContent = lastCmd + (time ? ' (' + time + ')' : '');
            } else {
                document.getElementById('status-last-cmd').textContent = 'None';
            }

            // Last trade
            const lastTrade = data.last_trade_time;
            document.getElementById('status-last-trade').textContent =
                lastTrade ? formatTime(lastTrade) : 'None';

            // Update button states
            document.getElementById('btn-pause').disabled = data.paused;
            document.getElementById('btn-resume').disabled = !data.paused;
            document.getElementById('btn-paper').disabled = data.mode === 'paper';
            document.getElementById('btn-live').disabled = data.mode === 'live';

            // Update risk input placeholders
            if (data.risk_limits) {
                document.getElementById('input-max-order').placeholder = data.risk_limits.max_order_size;
                document.getElementById('input-max-exposure').placeholder = data.risk_limits.max_exposure_per_market;
            }
        }

        function formatTime(isoString) {
            const date = new Date(isoString);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);

            if (diffMins < 1) return 'just now';
            if (diffMins < 60) return diffMins + 'm ago';
            if (diffMins < 1440) return Math.floor(diffMins / 60) + 'h ago';
            return Math.floor(diffMins / 1440) + 'd ago';
        }

        // =================================================================
        // Auto Refresh
        // =================================================================
        function startAutoRefresh() {
            stopAutoRefresh();
            fetchStatus();
            refreshInterval = setInterval(fetchStatus, 5000);
        }

        function stopAutoRefresh() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
                refreshInterval = null;
            }
        }

        // =================================================================
        // Actions
        // =================================================================
        async function pauseBot() {
            try {
                await apiCall('POST', '/pause');
                showMessage('Bot paused', 'success');
                fetchStatus();
            } catch (e) {
                showMessage('Failed to pause: ' + e.message, 'error');
            }
        }

        async function resumeBot() {
            try {
                await apiCall('POST', '/resume');
                showMessage('Bot resumed', 'success');
                fetchStatus();
            } catch (e) {
                showMessage('Failed to resume: ' + e.message, 'error');
            }
        }

        async function setMode(mode) {
            try {
                await apiCall('POST', '/mode/' + mode);
                showMessage('Mode set to ' + mode.toUpperCase(), 'success');
                fetchStatus();
            } catch (e) {
                showMessage('Failed to set mode: ' + e.message, 'error');
            }
        }

        async function updateRisk() {
            const maxOrder = document.getElementById('input-max-order').value;
            const maxExposure = document.getElementById('input-max-exposure').value;

            const body = {};
            if (maxOrder) body.max_order_size = parseFloat(maxOrder);
            if (maxExposure) body.max_exposure_per_market = parseFloat(maxExposure);

            if (Object.keys(body).length === 0) {
                showMessage('Enter at least one value', 'error');
                return;
            }

            try {
                await apiCall('POST', '/risk', body);
                showMessage('Risk limits updated', 'success');
                document.getElementById('input-max-order').value = '';
                document.getElementById('input-max-exposure').value = '';
                fetchStatus();
            } catch (e) {
                showMessage('Failed to update: ' + e.message, 'error');
            }
        }

        async function cancelAll() {
            if (!confirm('Cancel ALL open orders?')) return;

            try {
                await apiCall('POST', '/cancel-all');
                showMessage('All orders cancelled', 'success');
            } catch (e) {
                showMessage('Failed: ' + e.message, 'error');
            }
        }

        // =================================================================
        // Messages
        // =================================================================
        function showMessage(text, type) {
            const el = document.getElementById('message');
            el.textContent = text;
            el.className = 'message message-' + type;
            el.classList.remove('hidden');

            setTimeout(() => {
                el.classList.add('hidden');
            }, 3000);
        }

        // =================================================================
        // Start
        // =================================================================
        init();

        // Handle Enter key in token input
        document.getElementById('token-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') authenticate();
        });
    </script>
</body>
</html>
"""


@app.get("/ui", response_class=HTMLResponse)
async def get_ui():
    """Serve the web control panel."""
    return UI_HTML


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
