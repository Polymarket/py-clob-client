"""
Execution layer: wrapper around py-clob-client.

Provides a clean interface for the trading bot to interact with Polymarket.
All order placement, cancellation, and balance queries go through here.
"""

import logging
import os
from dataclasses import dataclass
from typing import Optional

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import (
    ApiCreds,
    BalanceAllowanceParams,
    AssetType,
    OrderArgs,
    OrderType,
)
from py_clob_client.constants import POLYGON
from py_clob_client.order_builder.constants import BUY, SELL

from bot.state import state

logger = logging.getLogger(__name__)


@dataclass
class TradeResult:
    """Result of a trade attempt."""
    success: bool
    order_id: Optional[str] = None
    error: Optional[str] = None
    details: Optional[dict] = None


class ExecutionEngine:
    """
    Wrapper around ClobClient for order execution.

    Handles:
    - Client initialization from environment variables
    - Order placement with safety checks
    - Order cancellation
    - Balance and exposure queries
    """

    def __init__(self):
        self.client: Optional[ClobClient] = None
        self._initialized = False

    def initialize(self) -> bool:
        """
        Initialize the CLOB client from environment variables.

        Required env vars:
        - POLY_PRIVATE_KEY: Your wallet private key
        - POLY_API_KEY: API key from Polymarket
        - POLY_API_SECRET: API secret
        - POLY_API_PASSPHRASE: API passphrase

        Optional:
        - POLY_HOST: CLOB host (default: https://clob.polymarket.com)

        Returns True if initialization succeeded, False otherwise.
        """
        try:
            private_key = os.environ.get("POLY_PRIVATE_KEY")
            api_key = os.environ.get("POLY_API_KEY")
            api_secret = os.environ.get("POLY_API_SECRET")
            api_passphrase = os.environ.get("POLY_API_PASSPHRASE")
            host = os.environ.get("POLY_HOST", "https://clob.polymarket.com")

            if not all([private_key, api_key, api_secret, api_passphrase]):
                logger.error("Missing required environment variables for CLOB client")
                logger.error("Required: POLY_PRIVATE_KEY, POLY_API_KEY, POLY_API_SECRET, POLY_API_PASSPHRASE")
                return False

            self.client = ClobClient(
                host=host,
                key=private_key,
                chain_id=POLYGON,
                creds=ApiCreds(
                    api_key=api_key,
                    api_secret=api_secret,
                    api_passphrase=api_passphrase,
                ),
            )

            # Verify connection
            self.client.get_ok()
            self._initialized = True
            logger.info("CLOB client initialized successfully")
            return True

        except Exception as e:
            logger.exception(f"Failed to initialize CLOB client: {e}")
            return False

    def is_initialized(self) -> bool:
        """Check if the client is initialized."""
        return self._initialized and self.client is not None

    def get_collateral_balance(self) -> Optional[float]:
        """Get USDC balance."""
        if not self.is_initialized():
            return None

        try:
            result = self.client.get_balance_allowance(
                params=BalanceAllowanceParams(asset_type=AssetType.COLLATERAL)
            )
            # Balance is returned as a string in atomic units (6 decimals for USDC)
            if result and hasattr(result, 'balance'):
                return float(result.balance) / 1e6
            return 0.0
        except Exception as e:
            logger.exception(f"Failed to get collateral balance: {e}")
            return None

    def get_token_balance(self, token_id: str) -> Optional[float]:
        """Get balance for a specific conditional token."""
        if not self.is_initialized():
            return None

        try:
            result = self.client.get_balance_allowance(
                params=BalanceAllowanceParams(
                    asset_type=AssetType.CONDITIONAL,
                    token_id=token_id,
                )
            )
            if result and hasattr(result, 'balance'):
                return float(result.balance)
            return 0.0
        except Exception as e:
            logger.exception(f"Failed to get token balance for {token_id}: {e}")
            return None

    def get_midpoint(self, token_id: str) -> Optional[float]:
        """Get current midpoint price for a token."""
        if not self.is_initialized():
            return None

        try:
            result = self.client.get_midpoint(token_id)
            if result and hasattr(result, 'mid'):
                return float(result.mid)
            return None
        except Exception as e:
            logger.exception(f"Failed to get midpoint for {token_id}: {e}")
            return None

    def get_order_book(self, token_id: str) -> Optional[dict]:
        """Get order book for a token."""
        if not self.is_initialized():
            return None

        try:
            book = self.client.get_order_book(token_id)
            return {
                "bids": [{"price": b.price, "size": b.size} for b in book.bids],
                "asks": [{"price": a.price, "size": a.size} for a in book.asks],
            }
        except Exception as e:
            logger.exception(f"Failed to get order book for {token_id}: {e}")
            return None

    def place_order(
        self,
        token_id: str,
        side: str,
        price: float,
        size: float,
        dry_run: bool = False,
    ) -> TradeResult:
        """
        Place a limit order.

        Args:
            token_id: The conditional token ID
            side: "BUY" or "SELL"
            price: Price between 0 and 1
            size: Number of shares
            dry_run: If True, validate but don't actually place the order

        Returns:
            TradeResult with success status and order details
        """
        # Validate inputs
        validation_error = self._validate_order(token_id, side, price, size)
        if validation_error:
            return TradeResult(success=False, error=validation_error)

        # Check risk limits
        risk_error = self._check_risk_limits(token_id, side, price, size)
        if risk_error:
            return TradeResult(success=False, error=risk_error)

        if dry_run:
            logger.info(f"[DRY RUN] Would place {side} order: {size} @ {price} for {token_id}")
            return TradeResult(
                success=True,
                details={"dry_run": True, "side": side, "price": price, "size": size}
            )

        if not self.is_initialized():
            return TradeResult(success=False, error="CLOB client not initialized")

        try:
            order_args = OrderArgs(
                token_id=token_id,
                price=price,
                size=size,
                side=BUY if side.upper() == "BUY" else SELL,
            )

            signed_order = self.client.create_order(order_args)
            response = self.client.post_order(signed_order, orderType=OrderType.GTC)

            # Update exposure tracking
            order_value = price * size
            if side.upper() == "BUY":
                state.add_exposure(token_id, order_value)

            state.record_trade()

            logger.info(f"Order placed: {side} {size} @ {price} for {token_id}")
            return TradeResult(
                success=True,
                order_id=response.get("orderID") if isinstance(response, dict) else None,
                details=response if isinstance(response, dict) else {"response": str(response)},
            )

        except Exception as e:
            logger.exception(f"Failed to place order: {e}")
            return TradeResult(success=False, error=str(e))

    def cancel_order(self, order_id: str) -> TradeResult:
        """Cancel a specific order."""
        if not self.is_initialized():
            return TradeResult(success=False, error="CLOB client not initialized")

        try:
            response = self.client.cancel(order_id)
            logger.info(f"Cancelled order: {order_id}")
            return TradeResult(success=True, order_id=order_id, details=response)
        except Exception as e:
            logger.exception(f"Failed to cancel order {order_id}: {e}")
            return TradeResult(success=False, error=str(e))

    def cancel_all_orders(self) -> TradeResult:
        """Cancel all open orders."""
        if not self.is_initialized():
            return TradeResult(success=False, error="CLOB client not initialized")

        try:
            response = self.client.cancel_all()
            logger.info("Cancelled all orders")
            return TradeResult(success=True, details=response)
        except Exception as e:
            logger.exception(f"Failed to cancel all orders: {e}")
            return TradeResult(success=False, error=str(e))

    def _validate_order(
        self, token_id: str, side: str, price: float, size: float
    ) -> Optional[str]:
        """Validate order parameters. Returns error message or None if valid."""
        if not token_id:
            return "token_id is required"

        if side.upper() not in ("BUY", "SELL"):
            return f"Invalid side: {side}. Must be BUY or SELL"

        if not (0 < price < 1):
            return f"Invalid price: {price}. Must be between 0 and 1 (exclusive)"

        if size <= 0:
            return f"Invalid size: {size}. Must be positive"

        return None

    def _check_risk_limits(
        self, token_id: str, side: str, price: float, size: float
    ) -> Optional[str]:
        """Check if order violates risk limits. Returns error message or None if OK."""
        limits = state.risk_limits
        order_value = price * size

        # Check max order size
        if order_value > limits.max_order_size:
            return f"Order value ${order_value:.2f} exceeds max order size ${limits.max_order_size:.2f}"

        # Check max exposure (only for BUY orders)
        if side.upper() == "BUY":
            current_exposure = state.get_exposure(token_id)
            new_exposure = current_exposure + order_value
            if new_exposure > limits.max_exposure_per_market:
                return (
                    f"New exposure ${new_exposure:.2f} would exceed "
                    f"max exposure ${limits.max_exposure_per_market:.2f} for this market"
                )

        return None


# Global execution engine instance
engine = ExecutionEngine()
