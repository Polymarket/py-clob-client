# RFQ Client Implementation Plan

This document outlines the implementation plan for adding RFQ (Request for Quote) functionality to the `py-clob-client`.

---

## Overview

The RFQ system enables negotiated trades between:
- **Takers**: Users who create RFQ requests seeking quotes
- **Makers**: Users who provide quotes in response to requests

This implementation adds a new `RfqClient` module that integrates with the existing `ClobClient` architecture.

---

## Phase 1: Data Types and Constants

### Checklist

- [ ] Create `py_clob_client/rfq/` directory
- [ ] Create `py_clob_client/rfq/__init__.py`
- [ ] Create `py_clob_client/rfq/rfq_types.py` with:
  - [ ] `RfqUserOrder` dataclass (token_id, price, side, size)
  - [ ] `CreateRfqRequestParams` dataclass (asset_in, asset_out, amount_in, amount_out, user_type)
  - [ ] `CreateRfqQuoteParams` dataclass
  - [ ] `ImproveRfqQuoteParams` dataclass
  - [ ] `CancelRfqRequestParams` dataclass
  - [ ] `CancelRfqQuoteParams` dataclass
  - [ ] `AcceptQuoteParams` dataclass
  - [ ] `ApproveOrderParams` dataclass
  - [ ] `GetRfqRequestsParams` dataclass
  - [ ] `GetRfqQuotesParams` dataclass
  - [ ] `GetRfqBestQuoteParams` dataclass
  - [ ] `RfqRequest` response dataclass
  - [ ] `RfqQuote` response dataclass
  - [ ] `RfqRequestResponse` dataclass
  - [ ] `RfqQuoteResponse` dataclass
  - [ ] `RfqPaginatedResponse` dataclass
- [ ] Add RFQ endpoints to `py_clob_client/endpoints.py`:
  - [ ] `CREATE_RFQ_REQUEST = "/rfq/request"`
  - [ ] `CANCEL_RFQ_REQUEST = "/rfq/request"`
  - [ ] `GET_RFQ_REQUESTS = "/rfq/data/requests"`
  - [ ] `CREATE_RFQ_QUOTE = "/rfq/quote"`
  - [ ] `IMPROVE_RFQ_QUOTE = "/rfq/quote"`
  - [ ] `CANCEL_RFQ_QUOTE = "/rfq/quote"`
  - [ ] `GET_RFQ_QUOTES = "/rfq/data/quotes"`
  - [ ] `GET_RFQ_BEST_QUOTE = "/rfq/data/best-quote"`
  - [ ] `RFQ_REQUESTS_ACCEPT = "/rfq/request/accept"`
  - [ ] `RFQ_QUOTE_APPROVE = "/rfq/quote/approve"`
  - [ ] `RFQ_CONFIG = "/rfq/config"`

---

## Phase 2: RFQ Helpers and Utilities

### Checklist

- [ ] Create `py_clob_client/rfq/rfq_helpers.py` with:
  - [ ] `parse_rfq_requests_params()` - Convert GetRfqRequestsParams to query dict
  - [ ] `parse_rfq_quotes_params()` - Convert GetRfqQuotesParams to query dict
  - [ ] `parse_units()` - Convert decimal string to smallest units (6 decimals)
  - [ ] `to_camel_case()` - Convert snake_case to camelCase for JSON
- [ ] Verify existing helpers can be reused:
  - [ ] `round_normal()` from `order_builder/helpers.py`
  - [ ] `round_down()` from `order_builder/helpers.py`
  - [ ] `ROUNDING_CONFIG` from `order_builder/helpers.py`
  - [ ] `decimal_places()` from `order_builder/helpers.py`

---

## Phase 3: HTTP Layer Enhancement

### Checklist

- [ ] Add `put()` method to `py_clob_client/http_helpers/helpers.py`:
  - [ ] Accept endpoint, headers, and data parameters
  - [ ] Use `_http_client.put()` with JSON body
  - [ ] Handle response parsing (JSON or text)
  - [ ] Handle errors with `PolyApiException`
- [ ] Verify L2 headers work with PUT method in `headers/headers.py`

---

## Phase 4: RFQ Client Implementation

### Checklist

- [ ] Create `py_clob_client/rfq/rfq_client.py` with `RfqClient` class
- [ ] Implement `__init__()` accepting parent ClobClient reference
- [ ] Implement `_ensure_l2_auth()` helper method
- [ ] Implement `_get_timestamp()` helper (server time or local)
- [ ] Implement request-side methods:
  - [ ] `create_rfq_request(user_order, options)` - Build request params from user order
  - [ ] `post_rfq_request(payload)` - POST to /rfq/request
  - [ ] `cancel_rfq_request(params)` - DELETE to /rfq/request
  - [ ] `get_rfq_requests(params)` - GET /rfq/data/requests
- [ ] Implement quote-side methods:
  - [ ] `create_rfq_quote(params)` - POST to /rfq/quote
  - [ ] `get_rfq_quotes(params)` - GET /rfq/data/quotes
  - [ ] `get_rfq_best_quote(params)` - GET /rfq/data/best-quote
  - [ ] `improve_rfq_quote(params)` - PUT to /rfq/quote
  - [ ] `cancel_rfq_quote(params)` - DELETE to /rfq/quote
- [ ] Implement trade execution methods:
  - [ ] `accept_rfq_quote(params)` - POST to /rfq/request/accept (taker side)
  - [ ] `approve_rfq_order(params)` - POST to /rfq/quote/approve (maker side)
- [ ] Implement configuration method:
  - [ ] `rfq_config()` - GET /rfq/config

---

## Phase 5: Integration with Main Client

### Checklist

- [ ] Modify `py_clob_client/client.py`:
  - [ ] Import `RfqClient` from rfq module
  - [ ] Add `self.rfq` attribute in `__init__()`
  - [ ] Initialize `RfqClient` with self as dependency provider
  - [ ] Add `use_server_time` configuration option if not present
- [ ] Update `py_clob_client/__init__.py`:
  - [ ] Export RFQ types
  - [ ] Export RfqClient (optional, for direct access)
- [ ] Update `py_clob_client/rfq/__init__.py`:
  - [ ] Export all public types
  - [ ] Export RfqClient

---

## Phase 6: Testing and Documentation

### Checklist

- [ ] Create `tests/test_rfq_types.py`:
  - [ ] Test dataclass instantiation
  - [ ] Test default values
- [ ] Create `tests/test_rfq_helpers.py`:
  - [ ] Test `parse_rfq_requests_params()`
  - [ ] Test `parse_rfq_quotes_params()`
  - [ ] Test `parse_units()` with various inputs
- [ ] Create `tests/test_rfq_client.py`:
  - [ ] Test `create_rfq_request()` calculations for BUY side
  - [ ] Test `create_rfq_request()` calculations for SELL side
  - [ ] Test rounding behavior for different tick sizes
  - [ ] Mock HTTP tests for each endpoint
- [ ] Create `examples/rfq_example.py`:
  - [ ] Example: Taker creates and manages a request
  - [ ] Example: Maker provides quotes
  - [ ] Example: Getting best quote
- [ ] Update README.md with RFQ usage documentation

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
