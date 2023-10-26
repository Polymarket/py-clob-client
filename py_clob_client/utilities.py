import hashlib

from .clob_types import OrderBookSummary, OrderSummary, TickSize


def parse_raw_orderbook_summary(raw_obs: any) -> OrderBookSummary:
    bids = []
    for bid in raw_obs["bids"]:
        bids.append(OrderSummary(size=bid["size"], price=bid["price"]))

    asks = []
    for ask in raw_obs["asks"]:
        asks.append(OrderSummary(size=ask["size"], price=ask["price"]))

    orderbookSummary = OrderBookSummary(
        market=raw_obs["market"],
        asset_id=raw_obs["asset_id"],
        bids=bids,
        asks=asks,
        hash=raw_obs["hash"],
    )

    return orderbookSummary


def generate_orderbook_summary_hash(orderbook: OrderBookSummary) -> str:
    orderbook.hash = ""
    hash = hashlib.sha1(str(orderbook.json).encode("utf-8")).hexdigest()
    orderbook.hash = hash
    return hash


def order_to_json(order, owner, orderType) -> dict:
    return {"order": order.dict(), "owner": owner, "orderType": orderType}


def is_tick_size_smaller(a: TickSize, b: TickSize) -> bool:
    return float(a) < float(b)
