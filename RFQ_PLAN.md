# RFQ Client Implementation Plan

This document outlines the implementation plan for adding RFQ (Request for Quote) functionality to the `py-clob-client`.

---

## Overview

The RFQ system enables negotiated trades between:
- **Takers**: Users who create RFQ requests seeking quotes
- **Makers**: Users who provide quotes in response to requests

This implementation adds a new `RfqClient` module that integrates with the existing `ClobClient` architecture.

---

## Phase 1: Data Types and Constants ✅ COMPLETED

### Checklist

- [x] Create `py_clob_client/rfq/` directory
- [x] Create `py_clob_client/rfq/__init__.py`
- [x] Create `py_clob_client/rfq/rfq_types.py` with:
  - [x] `RfqUserOrder` dataclass (token_id, price, side, size)
  - [x] `CreateRfqRequestParams` dataclass (asset_in, asset_out, amount_in, amount_out, user_type)
  - [x] `CreateRfqQuoteParams` dataclass
  - [x] `ImproveRfqQuoteParams` dataclass
  - [x] `CancelRfqRequestParams` dataclass
  - [x] `CancelRfqQuoteParams` dataclass
  - [x] `AcceptQuoteParams` dataclass
  - [x] `ApproveOrderParams` dataclass
  - [x] `GetRfqRequestsParams` dataclass
  - [x] `GetRfqQuotesParams` dataclass
  - [x] `GetRfqBestQuoteParams` dataclass
  - [x] `RfqRequest` response dataclass
  - [x] `RfqQuote` response dataclass
  - [x] `RfqRequestResponse` dataclass
  - [x] `RfqQuoteResponse` dataclass
  - [x] `RfqPaginatedResponse` dataclass
- [x] Add RFQ endpoints to `py_clob_client/endpoints.py`:
  - [x] `CREATE_RFQ_REQUEST = "/rfq/request"`
  - [x] `CANCEL_RFQ_REQUEST = "/rfq/request"`
  - [x] `GET_RFQ_REQUESTS = "/rfq/data/requests"`
  - [x] `CREATE_RFQ_QUOTE = "/rfq/quote"`
  - [x] `IMPROVE_RFQ_QUOTE = "/rfq/quote"`
  - [x] `CANCEL_RFQ_QUOTE = "/rfq/quote"`
  - [x] `GET_RFQ_QUOTES = "/rfq/data/quotes"`
  - [x] `GET_RFQ_BEST_QUOTE = "/rfq/data/best-quote"`
  - [x] `RFQ_REQUESTS_ACCEPT = "/rfq/request/accept"`
  - [x] `RFQ_QUOTE_APPROVE = "/rfq/quote/approve"`
  - [x] `RFQ_CONFIG = "/rfq/config"`

---

## Phase 2: RFQ Helpers and Utilities ✅ COMPLETED

### Checklist

- [x] Create `py_clob_client/rfq/rfq_helpers.py` with:
  - [x] `parse_rfq_requests_params()` - Convert GetRfqRequestsParams to query dict
  - [x] `parse_rfq_quotes_params()` - Convert GetRfqQuotesParams to query dict
  - [x] `parse_units()` - Convert decimal string to smallest units (6 decimals)
  - [x] `to_camel_case()` - Convert snake_case to camelCase for JSON
  - [x] `COLLATERAL_TOKEN_DECIMALS` constant (6)
  - [x] `CONDITIONAL_TOKEN_DECIMALS` constant (6)
- [x] Verify existing helpers can be reused:
  - [x] `round_normal()` from `order_builder/helpers.py`
  - [x] `round_down()` from `order_builder/helpers.py`
  - [x] `ROUNDING_CONFIG` from `order_builder/builder.py`
  - [x] `decimal_places()` from `order_builder/helpers.py`

---

## Phase 3: HTTP Layer Enhancement ✅ COMPLETED

### Checklist

- [x] Add `put()` method to `py_clob_client/http_helpers/helpers.py`:
  - [x] Accept endpoint, headers, and data parameters
  - [x] Uses existing `request()` function with PUT method
  - [x] Handle response parsing (JSON or text) - via existing `request()` function
  - [x] Handle errors with `PolyApiException` - via existing `request()` function
- [x] Verify L2 headers work with PUT method in `headers/headers.py`
  - [x] `create_level_2_headers()` accepts any method string via `RequestArgs`
  - [x] `build_hmac_signature()` handles any HTTP method

---

## Phase 4: RFQ Client Implementation ✅ COMPLETED

### Checklist

- [x] Create `py_clob_client/rfq/rfq_client.py` with `RfqClient` class
- [x] Implement `__init__()` accepting parent ClobClient reference
- [x] Implement `_ensure_l2_auth()` helper method
- [x] Implement `_get_l2_headers()` helper method
- [x] Implement `_build_url()` helper method
- [x] Implement request-side methods:
  - [x] `create_rfq_request(user_order, options)` - Build request params from user order
  - [x] `post_rfq_request(payload)` - POST to /rfq/request
  - [x] `cancel_rfq_request(params)` - DELETE to /rfq/request
  - [x] `get_rfq_requests(params)` - GET /rfq/data/requests
- [x] Implement quote-side methods:
  - [x] `create_rfq_quote(params)` - POST to /rfq/quote
  - [x] `get_rfq_quotes(params)` - GET /rfq/data/quotes
  - [x] `get_rfq_best_quote(params)` - GET /rfq/data/best-quote
  - [x] `improve_rfq_quote(params)` - PUT to /rfq/quote
  - [x] `cancel_rfq_quote(params)` - DELETE to /rfq/quote
- [x] Implement trade execution methods:
  - [x] `accept_rfq_quote(params)` - POST to /rfq/request/accept (taker side)
  - [x] `approve_rfq_order(params)` - POST to /rfq/quote/approve (maker side)
- [x] Implement configuration method:
  - [x] `rfq_config()` - GET /rfq/config
- [x] Update `py_clob_client/rfq/__init__.py` to export `RfqClient`

---

## Phase 5: Integration with Main Client ✅ COMPLETED

### Checklist

- [x] Modify `py_clob_client/client.py`:
  - [x] Import `RfqClient` from rfq module
  - [x] Add `self.rfq` attribute in `__init__()`
  - [x] Initialize `RfqClient` with self as dependency provider
- [x] Update `py_clob_client/__init__.py`:
  - [x] Export core types (ApiCreds, OrderArgs, etc.)
  - [x] Export RfqClient
  - [x] Export all RFQ input types
  - [x] Export all RFQ response types
- [x] Update `py_clob_client/rfq/__init__.py`:
  - [x] Export all public types (completed in Phase 4)
  - [x] Export RfqClient (completed in Phase 4)

---

## Phase 6: Testing and Documentation ✅ COMPLETED

### Checklist

- [x] Create `tests/rfq/__init__.py`
- [x] Create `tests/rfq/test_rfq_types.py`:
  - [x] Test dataclass instantiation for all 16 types
  - [x] Test default values
  - [x] Test RfqUserOrder, CreateRfqRequestParams, etc.
  - [x] Test response types (RfqRequest, RfqQuote, RfqPaginatedResponse)
- [x] Create `tests/rfq/test_rfq_helpers.py`:
  - [x] Test `parse_rfq_requests_params()` with various filters
  - [x] Test `parse_rfq_quotes_params()` with various filters
  - [x] Test `parse_units()` with various inputs (decimals, whole numbers, edge cases)
  - [x] Test `to_camel_case()` conversion
  - [x] Test constants (COLLATERAL_TOKEN_DECIMALS, CONDITIONAL_TOKEN_DECIMALS)
- [x] Create `tests/rfq/test_rfq_client.py`:
  - [x] Test `create_rfq_request()` calculations for BUY side
  - [x] Test `create_rfq_request()` calculations for SELL side
  - [x] Test rounding behavior for different tick sizes (0.1, 0.01, 0.001)
  - [x] Mock HTTP tests for all 12 RFQ endpoints
  - [x] Test L2 auth requirement
  - [x] Graceful skip when dependencies not available

**Note:** Tests require full dependencies to be installed. Run with:
```bash
pip install -r requirements.txt
pytest tests/rfq/ -v
```

---

## Technical Details

### Dependencies on Existing Code

| Component | Source File | Usage in RFQ |
|-----------|-------------|--------------|
| `Signer` | `signer.py` | Sign orders for accept/approve |
| `ApiCreds` | `clob_types.py` | L2 authentication |
| `create_level_2_headers()` | `headers/headers.py` | All API calls |
| `build_hmac_signature()` | `signing/hmac.py` | Signature creation |
| `OrderBuilder` | `order_builder/builder.py` | Create orders for accept/approve |
| `ROUNDING_CONFIG` | `order_builder/helpers.py` | Price/size rounding |
| `get()`, `post()`, `delete()` | `http_helpers/helpers.py` | HTTP requests |
| `PolyApiException` | `exceptions.py` | Error handling |

### Amount Calculation Logic

**For BUY orders (taker wants to buy tokens):**
- `asset_in` = token_id (what taker receives)
- `asset_out` = "0" (USDC, what taker pays)
- `amount_in` = size in token decimals
- `amount_out` = size × price in USDC decimals

**For SELL orders (taker wants to sell tokens):**
- `asset_in` = "0" (USDC, what taker receives)
- `asset_out` = token_id (what taker pays)
- `amount_in` = size × price in USDC decimals
- `amount_out` = size in token decimals

### JSON Field Naming Convention

Python uses snake_case, API expects camelCase:

| Python | JSON |
|--------|------|
| `request_id` | `requestId` |
| `quote_id` | `quoteId` |
| `asset_in` | `assetIn` |
| `asset_out` | `assetOut` |
| `amount_in` | `amountIn` |
| `amount_out` | `amountOut` |
| `user_type` | `userType` |

---

## File Structure

```
py_clob_client/
├── rfq/
│   ├── __init__.py          # Exports
│   ├── rfq_client.py        # RfqClient class (12 methods)
│   ├── rfq_types.py         # Data types (16 dataclasses)
│   └── rfq_helpers.py       # Utility functions
├── http_helpers/
│   └── helpers.py           # Add put() method
├── endpoints.py             # Add 11 RFQ endpoints
├── client.py                # Add self.rfq integration
└── __init__.py              # Update exports
```

---

## Estimated Scope

- **New files**: 4 (rfq module)
- **Modified files**: 4 (endpoints, http_helpers, client, __init__)
- **New dataclasses**: 16
- **New methods**: 12 (RfqClient) + 1 (put HTTP helper)
- **Test files**: 3
