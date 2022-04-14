from dataclasses import dataclass
from typing import Any


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
class LimitOrderArgs:
    price: float
    size: float
    side: str
    token_id: str

@dataclass
class MarketOrderArgs:
    size: float
    side: str
    token_id: str
    worst_price: float = None


@dataclass
class FilterParams:
    market: str = None
    max: int = None
    start_ts: int = None
    end_ts: int = None

