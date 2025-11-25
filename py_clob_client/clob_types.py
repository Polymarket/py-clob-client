from typing import Any, Literal, Optional
from dataclasses import dataclass, asdict
from json import dumps
from enum import Enum

from py_order_utils.model import (
    SignedOrder,
)

from .constants import ZERO_ADDRESS


# --- ENUMERATIONS ---

# Defines the accepted order execution types.
class OrderType(Enum):
    GTC = "GTC"  # Good Till Cancelled
    FOK = "FOK"  # Fill or Kill
    GTD = "GTD"  # Good Till Date (Expiration)
    FAK = "FAK"  # Fill and Kill


# --- API / NETWORK MODELS ---

@dataclass
class ApiCreds:
    """Credentials for API authentication."""
    api_key: str
    api_secret: str
    api_passphrase: str


@dataclass
class RequestArgs:
    """Arguments for generic API requests."""
    method: str
    request_path: str
    body: Any = None


@dataclass
class BookParams:
    """Parameters for querying the Order Book."""
    token_id: str
    side: str = ""


# --- ORDER ARGUMENTS ---

@dataclass
class BaseOrderArgs:
    """Common arguments shared by all order types."""
    token_id: str
    """
    TokenID of the Conditional Token asset being traded.
    """
    side: str
    """
    Side of the order (e.g., 'BUY' or 'SELL').
    """
    fee_rate_bps: int = 0
    """
    Fee rate, in basis points, charged to the order maker, calculated on proceeds.
    """
    nonce: int = 0
    """
    Nonce used for on-chain cancellations.
    """
    taker: str = ZERO_ADDRESS
    """
    Address of the order taker. The zero address is used to indicate a public order.
    """

@dataclass
class OrderArgs(BaseOrderArgs):
    """Arguments for creating a Limit Order (Price and Size specified)."""

    price: float
    """
    Price used to create the order.
    """
    size: float
    """
    Size in terms of the ConditionalToken (quantity).
    """
    expiration: int = 0
    """
    Timestamp after which the order is expired.
    """

@dataclass
class MarketOrderArgs(BaseOrderArgs):
    """Arguments for creating a Market Order (Amount specified)."""

    amount: float
    """
    For BUY orders: Collateral amount ($$$) to spend.
    For SELL orders: Shares (Conditional Tokens) to sell.
    """
    price: float = 0
    """
    Price used to create the order (often 0 for market orders, 
    but included for potential internal use).
    """
    order_type: OrderType = OrderType.FOK


# --- QUERY PARAMETERS ---

@dataclass
class TradeParams:
    """Parameters for filtering trade history."""
    id: Optional[str] = None
    maker_address: Optional[str] = None
    market: Optional[str] = None
    asset_id: Optional[str] = None
    before: Optional[int] = None
    after: Optional[int] = None


@dataclass
class OpenOrderParams:
    """Parameters for querying open orders."""
    id: Optional[str] = None
    market: Optional[str] = None
    asset_id: Optional[str] = None


@dataclass
class DropNotificationParams:
    """Parameters for dropping/managing notifications."""
    ids: Optional[list[str]] = None


# --- ORDER BOOK DATA MODELS ---

@dataclass
class OrderSummary:
    """Summary of a single bid or ask level in the order book."""
    price: Optional[str] = None
    size: Optional[str] = None

    # Note: Removed redundant __dict__ and json properties. 
    # Use asdict(self) and dumps(asdict(self)) externally for serialization.

@dataclass
class OrderBookSummary:
    """Snapshot of the Order Book state for a market."""
    market: Optional[str] = None
    asset_id: Optional[str] = None
    timestamp: Optional[str] = None
    bids: Optional[list[OrderSummary]] = None
    asks: Optional[list[OrderSummary]] = None
    min_order_size: Optional[str] = None
    neg_risk: Optional[bool] = None
    tick_size: Optional[str] = None
    hash: Optional[str] = None

    # Note: Removed redundant __dict__ and json properties. 
    # Use asdict(self) and dumps(asdict(self)) externally for serialization.


# --- ASSET & CONFIGURATION MODELS ---

class AssetType(Enum):
    """Defines the type of asset used in the exchange."""
    COLLATERAL = "COLLATERAL"
    CONDITIONAL = "CONDITIONAL"


@dataclass
class BalanceAllowanceParams:
    """Parameters for querying asset balance and allowance."""
    asset_type: Optional[AssetType] = None
    token_id: Optional[str] = None
    signature_type: int = -1


@dataclass
class OrderScoringParams:
    """Parameters for requesting a single order's scoring data."""
    orderId: str


@dataclass
class OrdersScoringParams:
    """Parameters for requesting multiple orders' scoring data."""
    orderIds: list[str]


TickSize = Literal["0.1", "0.01", "0.001", "0.0001"]


@dataclass
class CreateOrderOptions:
    """Mandatory options for creating an order."""
    tick_size: TickSize
    neg_risk: bool


@dataclass
class PartialCreateOrderOptions:
    """Optional options for creating an order."""
    tick_size: Optional[TickSize] = None
    neg_risk: Optional[bool] = None


@dataclass
class RoundConfig:
    """Configuration for rounding prices, sizes, and amounts."""
    price: float
    size: float
    amount: float


@dataclass
class ContractConfig:
    """Contract Configuration, defining core smart contract addresses."""
    exchange: str
    """
    The exchange contract responsible for matching orders.
    """
    collateral: str
    """
    The ERC20 token used as collateral for the exchange's markets.
    """
    conditional_tokens: str
    """
    The ERC1155 conditional tokens contract.
    """


@dataclass
class PostOrdersArgs:
    """Arguments for posting a signed order to the off-chain relayer."""
    order: SignedOrder
    orderType: OrderType = OrderType.GTC
