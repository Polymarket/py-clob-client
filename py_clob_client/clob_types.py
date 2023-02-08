from dataclasses import dataclass
from typing import Any
from dataclasses import dataclass, asdict
from json import dumps

from .constants import ZERO_ADDRESS


@dataclass
class ApiCreds:
    api_key: str
    api_secret: str
    api_passphrase: str


@dataclass
class RequestArgs:
    method: str
    request_path: str
    body: Any = None


@dataclass
class OrderArgs:
    token_id: str
    """
    TokenID of the Conditional token asset being traded
    """

    price: float
    """
    Price used to create the order
    """

    size: float
    """
    Size in terms of the ConditionalToken
    """

    side: str
    """
    Side of the order
    """

    fee_rate_bps: int = 0
    """
    Fee rate, in basis points, charged to the order maker, charged on proceeds
    """

    nonce: int = 0
    """
    Nonce used for onchain cancellations
    """

    expiration: int = 0
    """
    Timestamp after which the order is expired.
    """

    taker: str = ZERO_ADDRESS
    """
    Address of the order taker. The zero address is used to indicate a public order
    """


@dataclass
class FilterParams:
    market: str = None
    maker: str = None
    taker: str = None
    id: str = None
    limit: int = None
    before: int = None
    after: int = None
    owner: str = None


@dataclass
class TradeNotificationParams:
    index: int = None


@dataclass
class OrderSummary:
    price: str = None
    size: str = None

    @property
    def __dict__(self):
        return asdict(self)

    @property
    def json(self):
        return dumps(self.__dict__)


@dataclass
class OrderBookSummary:
    market: str = None
    asset_id: str = None
    bids: list[OrderSummary] = None
    asks: list[OrderSummary] = None
    hash: str = None

    @property
    def __dict__(self):
        return asdict(self)

    @property
    def json(self):
        return dumps(self.__dict__, separators=(",", ":"))
