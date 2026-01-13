"""
Shared mutable state for the trading bot.

This module holds all runtime state that can be modified via the HTTP API.
Thread-safe access is ensured via a lock.
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class RiskLimits:
    """Risk management parameters."""
    max_order_size: float = 100.0  # Max size per order in dollars
    max_exposure_per_market: float = 500.0  # Max total exposure per market


@dataclass
class BotState:
    """
    Central state container for the trading bot.

    All fields are protected by _lock for thread-safe access.
    """
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    # Control flags
    paused: bool = True  # Start paused for safety
    mode: str = "paper"  # "paper" or "live"

    # Risk limits
    risk_limits: RiskLimits = field(default_factory=RiskLimits)

    # Tracking
    start_time: datetime = field(default_factory=datetime.utcnow)
    last_command: Optional[str] = None
    last_command_time: Optional[datetime] = None
    last_trade_time: Optional[datetime] = None

    # Current positions/exposure tracking (token_id -> exposure in dollars)
    exposure: dict = field(default_factory=dict)

    def set_paused(self, paused: bool) -> None:
        """Set the paused state."""
        with self._lock:
            self.paused = paused
            self._record_command("pause" if paused else "resume")

    def set_mode(self, mode: str) -> None:
        """Set trading mode (paper/live)."""
        if mode not in ("paper", "live"):
            raise ValueError(f"Invalid mode: {mode}. Must be 'paper' or 'live'.")
        with self._lock:
            self.mode = mode
            self._record_command(f"mode:{mode}")

    def set_risk_limits(self, max_order_size: Optional[float] = None,
                        max_exposure_per_market: Optional[float] = None) -> None:
        """Update risk limits."""
        with self._lock:
            if max_order_size is not None:
                self.risk_limits.max_order_size = max_order_size
            if max_exposure_per_market is not None:
                self.risk_limits.max_exposure_per_market = max_exposure_per_market
            self._record_command("risk:update")

    def record_trade(self) -> None:
        """Record that a trade was executed."""
        with self._lock:
            self.last_trade_time = datetime.utcnow()

    def get_exposure(self, token_id: str) -> float:
        """Get current exposure for a token."""
        with self._lock:
            return self.exposure.get(token_id, 0.0)

    def add_exposure(self, token_id: str, amount: float) -> None:
        """Add to exposure for a token."""
        with self._lock:
            current = self.exposure.get(token_id, 0.0)
            self.exposure[token_id] = current + amount

    def reduce_exposure(self, token_id: str, amount: float) -> None:
        """Reduce exposure for a token."""
        with self._lock:
            current = self.exposure.get(token_id, 0.0)
            self.exposure[token_id] = max(0.0, current - amount)

    def _record_command(self, command: str) -> None:
        """Record a command (must be called with lock held)."""
        self.last_command = command
        self.last_command_time = datetime.utcnow()

    def get_status(self) -> dict:
        """Get current status as a dictionary."""
        with self._lock:
            uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
            return {
                "paused": self.paused,
                "mode": self.mode,
                "uptime_seconds": int(uptime_seconds),
                "uptime_human": _format_duration(uptime_seconds),
                "last_command": self.last_command,
                "last_command_time": self.last_command_time.isoformat() if self.last_command_time else None,
                "last_trade_time": self.last_trade_time.isoformat() if self.last_trade_time else None,
                "risk_limits": {
                    "max_order_size": self.risk_limits.max_order_size,
                    "max_exposure_per_market": self.risk_limits.max_exposure_per_market,
                },
                "exposure": dict(self.exposure),
            }


def _format_duration(seconds: float) -> str:
    """Format seconds into a human-readable duration."""
    seconds = int(seconds)
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")

    return " ".join(parts)


# Global state instance
state = BotState()
