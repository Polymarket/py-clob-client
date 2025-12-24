import hashlib
from typing import Any, Dict, List, Optional
from decimal import Decimal # Recommended for financial precision

# Assuming clob_types defines DecimalNumber, OrderBookSummary, OrderSummary, TickSize
from .clob_types import OrderBookSummary, OrderSummary, TickSize

# Define type for raw data input
RawOrderBookData = Dict[str, Any]

def parse_raw_orderbook_summary(raw_obs: RawOrderBookData) -> OrderBookSummary:
    """
    Parses a raw dictionary containing order book data into a structured OrderBookSummary object.
    Uses list comprehensions for concise and performant parsing of bid/ask lists.
    """
    # Use list comprehension for efficient parsing
    bids: List[OrderSummary] = [
        OrderSummary(size=bid["size"], price=bid["price"]) for bid in raw_obs.get("bids", [])
    ]

    asks: List[OrderSummary] = [
        OrderSummary(size=ask["size"], price=ask["price"]) for ask in raw_obs.get("asks", [])
    ]

    # Initialize the OrderBookSummary using direct dictionary unpacking 
    # if the keys match the model fields (assuming a Pydantic/dataclass model).
    # This is a cleaner alternative to repeated key lookups.
    return OrderBookSummary(
        market=raw_obs["market"],
        asset_id=raw_obs["asset_id"],
        timestamp=raw_obs["timestamp"],
        min_order_size=raw_obs["min_order_size"],
        neg_risk=raw_obs["neg_risk"],
        tick_size=raw_obs["tick_size"],
        hash=raw_obs.get("hash", ""), # Use .get() for optional fields
        bids=bids,
        asks=asks,
    )


def generate_orderbook_summary_hash(orderbook: OrderBookSummary) -> str:
    """
    Generates a cryptographic hash (SHA-256 recommended) for the order book summary.
    
    IMPORTANT: This function is now PURE (no side effects) and does not modify 
    the input object's hash field. The calling code should set the hash externally.
    
    The hash calculation relies on the structured JSON representation of the orderbook 
    (excluding the hash field itself) to ensure consistency.
    """
    # Create a mutable copy and clear the hash field before generating the JSON string
    # to prevent the hash from being included in its own calculation.
    # Assuming 'orderbook.json' is a method that returns the JSON string.
    temp_orderbook = orderbook.copy() 
    temp_orderbook.hash = ""
    
    # Use SHA256 for modern cryptographic security.
    # Assuming orderbook model provides a predictable JSON serialization (e.g., sorted keys).
    hash_input = temp_orderbook.json().encode("utf-8")
    
    return hashlib.sha256(hash_input).hexdigest()


def order_to_json(order: Any, owner: str, order_type: str) -> dict:
    """
    Converts an order object into a standardized JSON-like dictionary format.
    Ensures 'orderType' follows Python's naming convention (snake_case).
    """
    return {"order": order.dict(), "owner": owner, "order_type": order_type}


def is_tick_size_smaller(a: TickSize, b: TickSize) -> bool:
    """
    Compares two tick sizes. 
    NOTE: In a production financial system, TickSize should be a Decimal or integer type 
    to avoid float precision issues. Comparison should be exact.
    """
    # Assuming TickSize is implemented using a high-precision type like Decimal
    return Decimal(str(a)) < Decimal(str(b))


def price_valid(price: Decimal, tick_size: TickSize) -> bool:
    """
    Checks if the price is valid according to the tick size constraints.
    It must be greater than or equal to the tick size and less than 1 - tick_size.
    Uses Decimal for accurate financial comparison.
    """
    decimal_price = Decimal(str(price))
    decimal_tick = Decimal(str(tick_size))

    # Ensures price is >= tick_size AND price is <= (1 - tick_size)
    return decimal_price >= decimal_tick and decimal_price <= (Decimal('1') - decimal_tick)
