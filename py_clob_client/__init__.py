"""Python client for interacting with Polymarket's CLOB.

This package exposes classes and type definitions for working with the Polymarket central limit order book API. Use `ClobClient` to authenticate and make requests, and refer to the various data classes in `clob_types` for constructing orders and RFQ messages.

Example:
    from py_clob_client import ClobClient, OrderArgs, OrderType

    client = ClobClient(api_key="...", api_secret="...")
    order = OrderArgs(...)
    client.create_order(order)
"""
from .client import ClobClient
from .clob_types import (
    ApiCreds,
    OrderArgs,
    MarketOrderArgs,
    OrderType,
    TickSize,
    BookParams,
    TradeParams,
    OpenOrderParams,
    BalanceAllowanceParams,
    AssetType,
    PartialCreateOrderOptions,
    CreateOrderOptions,
)

# RFQ exports
from .rfq import (
    RfqClient,
    RfqUserRequest,
    RfqUserQuote,
    CreateRfqRequestParams,
    CreateRfqQuoteParams,
    CancelRfqRequestParams,
    CancelRfqQuoteParams,
    AcceptQuoteParams,
    ApproveOrderParams,
    GetRfqRequestsParams,
    GetRfqQuotesParams,
    GetRfqBestQuoteParams,
    RfqRequest,
    RfqQuote,
    RfqRequestResponse,
    RfqQuoteResponse,
    RfqPaginatedResponse,
)

__all__ = [
    # Main client
    "ClobClient",
    # Core types
    "ApiCreds",
    "OrderArgs",
    "MarketOrderArgs",
    "OrderType",
    "TickSize",
    "BookParams",
    "TradeParams",
    "OpenOrderParams",
    "BalanceAllowanceParams",
    "AssetType",
    "PartialCreateOrderOptions",
    "CreateOrderOptions",
    # RFQ client
    "RfqClient",
    # RFQ input types
    "RfqUserRequest",
    "RfqUserQuote",
    "CreateRfqRequestParams",
    "CreateRfqQuoteParams",
    "CancelRfqRequestParams",
    "CancelRfqQuoteParams",
    "AcceptQuoteParams",
    "ApproveOrderParams",
    "GetRfqRequestsParams",
    "GetRfqQuotesParams",
    "GetRfqBestQuoteParams",
    # RFQ response types
    "RfqRequest",
    "RfqQuote",
    "RfqRequestResponse",
    "RfqQuoteResponse",
    "RfqPaginatedResponse",
]
