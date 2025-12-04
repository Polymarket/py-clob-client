# RFQ Client Implementation Specification

This document provides a complete specification for implementing an RFQ (Request for Quote) client for the Polymarket CLOB API. Use this as a reference when implementing a compatible client in any language (e.g., Python).

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Configuration & Constants](#configuration--constants)
4. [Authentication](#authentication)
5. [Data Types](#data-types)
6. [API Endpoints](#api-endpoints)
7. [Method Implementations](#method-implementations)
8. [Utility Functions](#utility-functions)
9. [Complete Flow Examples](#complete-flow-examples)

---

## Overview

The RFQ system enables negotiated trades between:
- **Takers**: Users who create RFQ requests seeking quotes
- **Makers**: Users who provide quotes in response to requests

### Core Concepts

- **RFQ Request**: A taker's intent to trade at a specific price/size
- **RFQ Quote**: A maker's response offering to fill the request
- **Asset "0"**: Represents USDC (collateral token)
- **Asset TokenID**: Represents the conditional token being traded

---

## Architecture

### Dependencies

The RFQ client requires these capabilities from the parent CLOB client:

```python
class RfqDeps:
    host: str                    # API base URL
    signer: Signer               # Wallet for signing (eth account)
    creds: ApiKeyCreds           # API key credentials
    user_type: int               # Signature type (0=EOA, 1=Contract)
    use_server_time: bool        # Whether to use server time for signatures

    # Methods from parent client
    def get_server_time() -> int: ...
    def get_tick_size(token_id: str) -> TickSize: ...
    def resolve_tick_size(token_id: str, tick_size: Optional[TickSize]) -> TickSize: ...
    def create_order(user_order: UserOrder, options: CreateOrderOptions) -> SignedOrder: ...

    # HTTP methods (should handle geo_block_token injection)
    def get(endpoint: str, headers: dict, params: dict) -> Any: ...
    def post(endpoint: str, headers: dict, data: dict) -> Any: ...
    def put(endpoint: str, headers: dict, data: dict) -> Any: ...
    def delete(endpoint: str, headers: dict, data: dict) -> Any: ...
```

### Interface

```python
class IRfqClient:
    # Request-side methods
    def create_rfq_request(user_order: RfqUserOrder, options: CreateOrderOptions) -> CreateRfqRequestParams
    def post_rfq_request(payload: CreateRfqRequestParams) -> RfqRequestResponse
    def cancel_rfq_request(request: CancelRfqRequestParams) -> str  # Returns "OK"
    def get_rfq_requests(params: GetRfqRequestsParams) -> RfqRequestsResponse

    # Quote-side methods
    def create_rfq_quote(quote: CreateRfqQuoteParams) -> RfqQuoteResponse
    def get_rfq_quotes(params: GetRfqQuotesParams) -> RfqQuotesResponse
    def get_rfq_best_quote(params: GetRfqBestQuoteParams) -> RfqQuote
    def improve_rfq_quote(quote: ImproveRfqQuoteParams) -> str  # Returns "OK"
    def cancel_rfq_quote(quote: CancelRfqQuoteParams) -> str  # Returns "OK"

    # Trade execution
    def accept_rfq_quote(payload: AcceptQuoteParams) -> str  # Returns "OK"
    def approve_rfq_order(payload: ApproveOrderParams) -> str  # Returns "OK"

    # Configuration
    def rfq_config() -> Any
```

---

## Configuration & Constants

### Token Decimals

```python
COLLATERAL_TOKEN_DECIMALS = 6  # USDC has 6 decimals
CONDITIONAL_TOKEN_DECIMALS = 6
```

### Tick Size Rounding Configuration

Different tick sizes require different decimal precision for price, size, and amount calculations:

```python
ROUNDING_CONFIG = {
    "0.1": {
        "price": 1,   # 1 decimal place for price
        "size": 2,    # 2 decimal places for size
        "amount": 3,  # 3 decimal places for calculated amounts
    },
    "0.01": {
        "price": 2,
        "size": 2,
        "amount": 4,
    },
    "0.001": {
        "price": 3,
        "size": 2,
        "amount": 5,
    },
    "0.0001": {
        "price": 4,
        "size": 2,
        "amount": 6,
    },
}
```

### Side Enum

```python
class Side:
    BUY = "BUY"
    SELL = "SELL"
```

### Signature Types (User Types)

```python
class SignatureType:
    EOA = 0        # Externally Owned Account
    POLY_PROXY = 1 # Contract/Proxy wallet
    POLY_GNOSIS_SAFE = 2
```

---

## Authentication

All RFQ endpoints require L2 authentication using API key credentials.

### API Key Credentials Structure

```python
@dataclass
class ApiKeyCreds:
    key: str        # API key
    secret: str     # Base64-encoded secret
    passphrase: str # Passphrase
```

### L2 Header Args Structure

```python
@dataclass
class L2HeaderArgs:
    method: str       # HTTP method: "GET", "POST", "PUT", "DELETE"
    request_path: str # API endpoint path (e.g., "/rfq/request")
    body: str = None  # JSON string of request body (optional)
```

### Building HMAC Signature

The signature is created using HMAC-SHA256:

```python
import hmac
import hashlib
import base64

def build_poly_hmac_signature(
    secret: str,
    timestamp: int,
    method: str,
    request_path: str,
    body: str = None
) -> str:
    """
    Build the canonical Polymarket CLOB HMAC signature.

    Args:
        secret: Base64-encoded API secret
        timestamp: Unix timestamp in seconds
        method: HTTP method (GET, POST, PUT, DELETE)
        request_path: API endpoint path
        body: JSON string of request body (optional)

    Returns:
        URL-safe base64-encoded HMAC signature
    """
    # Build message: timestamp + method + path + body
    message = f"{timestamp}{method}{request_path}"
    if body is not None:
        message += body

    # Decode base64 secret
    secret_bytes = base64.b64decode(secret)

    # Create HMAC-SHA256
    hmac_obj = hmac.new(secret_bytes, message.encode('utf-8'), hashlib.sha256)
    signature = base64.b64encode(hmac_obj.digest()).decode('utf-8')

    # Convert to URL-safe base64 (keep '=' suffix)
    # Replace '+' with '-'
    # Replace '/' with '_'
    signature = signature.replace('+', '-').replace('/', '_')

    return signature
```

### Creating L2 Headers

```python
def create_l2_headers(
    signer_address: str,
    creds: ApiKeyCreds,
    l2_header_args: L2HeaderArgs,
    timestamp: int = None
) -> dict:
    """
    Create L2 authentication headers for RFQ API requests.

    Args:
        signer_address: Ethereum address of the signer
        creds: API key credentials
        l2_header_args: Method, path, and optional body
        timestamp: Optional timestamp (uses current time if not provided)

    Returns:
        Dictionary of headers
    """
    if timestamp is None:
        timestamp = int(time.time())

    signature = build_poly_hmac_signature(
        creds.secret,
        timestamp,
        l2_header_args.method,
        l2_header_args.request_path,
        l2_header_args.body
    )

    return {
        "POLY_ADDRESS": signer_address,
        "POLY_SIGNATURE": signature,
        "POLY_TIMESTAMP": str(timestamp),
        "POLY_API_KEY": creds.key,
        "POLY_PASSPHRASE": creds.passphrase,
    }
```

### Standard HTTP Headers

In addition to authentication headers, include these standard headers:

```python
STANDARD_HEADERS = {
    "User-Agent": "@polymarket/clob-client",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
}

# For GET requests, also add:
GET_HEADERS = {
    **STANDARD_HEADERS,
    "Accept-Encoding": "gzip",
}
```

---

## Data Types

### Input Types

#### RfqUserOrder (Simplified user input)

```python
@dataclass
class RfqUserOrder:
    token_id: str   # Token ID of the conditional token
    price: float    # Price (0 < price < 1)
    side: str       # "BUY" or "SELL"
    size: float     # Size in conditional tokens
```

#### CreateRfqRequestParams (Server payload)

```python
@dataclass
class CreateRfqRequestParams:
    asset_in: str    # Asset being paid (token ID or "0" for USDC)
    asset_out: str   # Asset being received
    amount_in: str   # Amount being paid (in smallest units, as string)
    amount_out: str  # Amount being received (in smallest units, as string)
    user_type: int   # Signature type (0 or 1)
```

#### CreateRfqQuoteParams

```python
@dataclass
class CreateRfqQuoteParams:
    request_id: str  # ID of the RFQ request being quoted
    asset_in: str    # Asset the maker is paying
    asset_out: str   # Asset the maker is receiving
    amount_in: str   # Amount maker is paying (smallest units)
    amount_out: str  # Amount maker is receiving (smallest units)
    # user_type is auto-filled by the client
```

#### ImproveRfqQuoteParams

```python
@dataclass
class ImproveRfqQuoteParams:
    quote_id: str    # ID of the quote to improve
    amount_out: str  # New improved amount_out (smallest units)
```

#### CancelRfqQuoteParams

```python
@dataclass
class CancelRfqQuoteParams:
    quote_id: str    # ID of the quote to cancel
```

#### CancelRfqRequestParams

```python
@dataclass
class CancelRfqRequestParams:
    request_id: str  # ID of the request to cancel
```

#### AcceptQuoteParams

```python
@dataclass
class AcceptQuoteParams:
    request_id: str  # ID of the RFQ request
    quote_id: str    # ID of the quote being accepted
    expiration: int  # Unix timestamp for order expiration
```

#### ApproveOrderParams

```python
@dataclass
class ApproveOrderParams:
    request_id: str  # ID of the RFQ request
    quote_id: str    # ID of the quote being approved
    expiration: int  # Unix timestamp for order expiration
```

#### GetRfqRequestsParams

```python
@dataclass
class GetRfqRequestsParams:
    request_ids: List[str] = None    # Filter by specific request IDs
    user_address: str = None         # Filter by user address
    states: List[str] = None         # Filter by states
    state: str = None                # Single state filter ("active"/"inactive")
    markets: List[str] = None        # Filter by market condition IDs
    size_min: float = None           # Minimum size filter
    size_max: float = None           # Maximum size filter
    size_usdc_min: float = None      # Minimum USDC size
    size_usdc_max: float = None      # Maximum USDC size
    price_min: float = None          # Minimum price
    price_max: float = None          # Maximum price
    sort_by: str = None              # Sort field
    sort_dir: str = None             # "asc" or "desc"
    limit: int = None                # Pagination limit
    offset: str = None               # Pagination cursor (base64 encoded)
```

#### GetRfqQuotesParams

```python
@dataclass
class GetRfqQuotesParams:
    quote_ids: List[str] = None      # Filter by specific quote IDs
    request_ids: List[str] = None    # Filter by request IDs
    user_address: str = None         # Filter by user address
    states: List[str] = None         # Filter by states
    state: str = None                # Single state filter
    markets: List[str] = None        # Filter by markets
    size_min: float = None
    size_max: float = None
    size_usdc_min: float = None
    size_usdc_max: float = None
    price_min: float = None
    price_max: float = None
    sort_by: str = None
    sort_dir: str = None
    limit: int = None
    offset: str = None
```

#### GetRfqBestQuoteParams

```python
@dataclass
class GetRfqBestQuoteParams:
    request_id: str = None  # Request ID to get best quote for
```

### Response Types

#### RfqRequest

```python
@dataclass
class RfqRequest:
    request_id: str          # Unique request identifier
    user_address: str        # Address of the requester
    proxy_address: str       # Proxy address if applicable
    token: str               # Token ID being traded
    complement: str          # Complement token ID
    condition: str           # Condition ID (market)
    side: str                # "BUY" or "SELL"
    size_in: str             # Size of asset_in
    size_out: str            # Size of asset_out
    price: float             # Price
    accepted_quote_id: str   # ID of accepted quote (if any)
    state: str               # Request state
    expiry: datetime         # Expiration timestamp
    created_at: datetime     # Creation timestamp
    updated_at: datetime     # Last update timestamp
```

#### RfqQuote

```python
@dataclass
class RfqQuote:
    quote_id: str            # Unique quote identifier
    request_id: str          # Associated request ID
    user_address: str        # Address of the quoter
    proxy_address: str       # Proxy address if applicable
    complement: str          # Complement token ID
    condition: str           # Condition ID (market)
    token: str               # Token ID
    side: str                # "BUY" or "SELL"
    size_in: str             # Size of asset_in
    size_out: str            # Size of asset_out
    price: float             # Quote price
    state: str               # Quote state
    expiry: datetime         # Expiration timestamp
    created_at: datetime     # Creation timestamp
    updated_at: datetime     # Last update timestamp
```

#### RfqRequestResponse

```python
@dataclass
class RfqRequestResponse:
    request_id: str          # Created request ID
    error: str = None        # Error message if failed
```

#### RfqQuoteResponse

```python
@dataclass
class RfqQuoteResponse:
    quote_id: str            # Created quote ID
    error: str = None        # Error message if failed
```

#### RfqPaginatedResponse

```python
@dataclass
class RfqPaginatedResponse:
    data: List[Any]          # Array of results
    next_cursor: str         # Cursor for next page
    limit: int               # Page limit
    count: int               # Number of results in this page
    total_count: int = None  # Total count (optional)
```

---

## API Endpoints

```python
# RFQ Endpoints
CREATE_RFQ_REQUEST = "/rfq/request"      # POST - Create request
CANCEL_RFQ_REQUEST = "/rfq/request"      # DELETE - Cancel request
GET_RFQ_REQUESTS = "/rfq/data/requests"  # GET - Get requests

CREATE_RFQ_QUOTE = "/rfq/quote"          # POST - Create quote
IMPROVE_RFQ_QUOTE = "/rfq/quote"         # PUT - Improve quote
CANCEL_RFQ_QUOTE = "/rfq/quote"          # DELETE - Cancel quote

RFQ_REQUESTS_ACCEPT = "/rfq/request/accept"  # POST - Accept quote (taker)
RFQ_QUOTE_APPROVE = "/rfq/quote/approve"     # POST - Approve order (maker)

GET_RFQ_QUOTES = "/rfq/data/quotes"          # GET - Get quotes
GET_RFQ_BEST_QUOTE = "/rfq/data/best-quote"  # GET - Get best quote

RFQ_CONFIG = "/rfq/config"               # GET - Get RFQ configuration
```

---

## Method Implementations

### 1. create_rfq_request

Converts a simplified user order into RFQ request parameters.

```python
async def create_rfq_request(
    self,
    user_order: RfqUserOrder,
    options: CreateOrderOptions = None
) -> CreateRfqRequestParams:
    """
    Create RFQ request parameters from a user order.

    This method:
    1. Resolves the tick size for the token
    2. Rounds price and size according to tick size rules
    3. Calculates amountIn and amountOut based on side
    4. Returns parameters ready to post to the server

    Args:
        user_order: Simplified order with tokenID, price, side, size
        options: Optional tick size override

    Returns:
        CreateRfqRequestParams ready for posting
    """
    token_id = user_order.token_id
    price = user_order.price
    side = user_order.side
    size = user_order.size

    # Resolve tick size (from options or fetch from server)
    tick_size = await self.deps.resolve_tick_size(
        token_id,
        options.tick_size if options else None
    )

    # Get rounding configuration
    round_config = ROUNDING_CONFIG[tick_size]

    # Round price and size
    rounded_price = round_normal(price, round_config["price"])
    rounded_size = round_down(size, round_config["size"])

    # Format with correct decimal places
    rounded_price_str = f"{rounded_price:.{round_config['price']}f}"
    rounded_size_str = f"{rounded_size:.{round_config['size']}f}"

    # Parse back to numbers
    size_num = float(rounded_size_str)
    price_num = float(rounded_price_str)

    # Calculate amounts based on side
    if side == Side.BUY:
        # Buying tokens: pay USDC, receive tokens
        # amountIn = size (tokens to receive)
        # amountOut = size * price (USDC to pay)
        amount_in = parse_units(rounded_size_str, COLLATERAL_TOKEN_DECIMALS)

        usdc_amount = size_num * price_num
        usdc_amount_str = f"{usdc_amount:.{round_config['amount']}f}"
        amount_out = parse_units(usdc_amount_str, COLLATERAL_TOKEN_DECIMALS)

        asset_in = token_id
        asset_out = "0"  # USDC
    else:
        # Selling tokens: pay tokens, receive USDC
        # amountIn = size * price (USDC to receive)
        # amountOut = size (tokens to pay)
        usdc_amount = size_num * price_num
        usdc_amount_str = f"{usdc_amount:.{round_config['amount']}f}"
        amount_in = parse_units(usdc_amount_str, COLLATERAL_TOKEN_DECIMALS)

        amount_out = parse_units(rounded_size_str, COLLATERAL_TOKEN_DECIMALS)

        asset_in = "0"  # USDC
        asset_out = token_id

    return CreateRfqRequestParams(
        asset_in=asset_in,
        asset_out=asset_out,
        amount_in=str(amount_in),
        amount_out=str(amount_out),
        user_type=self.deps.user_type,
    )
```

### 2. post_rfq_request

Posts an RFQ request to the server.

```python
async def post_rfq_request(
    self,
    payload: CreateRfqRequestParams
) -> RfqRequestResponse:
    """
    Post an RFQ request to the server.

    Args:
        payload: Request parameters from create_rfq_request

    Returns:
        RfqRequestResponse with requestId
    """
    self._ensure_l2_auth()

    endpoint = "/rfq/request"
    body = json.dumps({
        "assetIn": payload.asset_in,
        "assetOut": payload.asset_out,
        "amountIn": payload.amount_in,
        "amountOut": payload.amount_out,
        "userType": payload.user_type,
    })

    l2_header_args = L2HeaderArgs(
        method="POST",
        request_path=endpoint,
        body=body,
    )

    timestamp = await self.deps.get_server_time() if self.deps.use_server_time else None
    headers = create_l2_headers(
        self.deps.signer.address,
        self.deps.creds,
        l2_header_args,
        timestamp,
    )

    return await self.deps.post(
        f"{self.deps.host}{endpoint}",
        headers=headers,
        data=payload.__dict__,
    )
```

### 3. cancel_rfq_request

Cancels an existing RFQ request.

```python
async def cancel_rfq_request(
    self,
    request: CancelRfqRequestParams
) -> str:
    """
    Cancel an RFQ request.

    Args:
        request: Contains requestId to cancel

    Returns:
        "OK" on success
    """
    self._ensure_l2_auth()

    endpoint = "/rfq/request"
    body = json.dumps({"requestId": request.request_id})

    l2_header_args = L2HeaderArgs(
        method="DELETE",
        request_path=endpoint,
        body=body,
    )

    timestamp = await self.deps.get_server_time() if self.deps.use_server_time else None
    headers = create_l2_headers(
        self.deps.signer.address,
        self.deps.creds,
        l2_header_args,
        timestamp,
    )

    return await self.deps.delete(
        f"{self.deps.host}{endpoint}",
        headers=headers,
        data={"requestId": request.request_id},
    )
```

### 4. get_rfq_requests

Gets RFQ requests with optional filtering.

```python
async def get_rfq_requests(
    self,
    params: GetRfqRequestsParams = None
) -> RfqRequestsResponse:
    """
    Get RFQ requests with optional filtering.

    Args:
        params: Optional filter parameters

    Returns:
        Paginated response with RFQ requests
    """
    self._ensure_l2_auth()

    endpoint = "/rfq/data/requests"

    l2_header_args = L2HeaderArgs(
        method="GET",
        request_path=endpoint,
    )

    timestamp = await self.deps.get_server_time() if self.deps.use_server_time else None
    headers = create_l2_headers(
        self.deps.signer.address,
        self.deps.creds,
        l2_header_args,
        timestamp,
    )

    query_params = parse_rfq_requests_params(params)

    return await self.deps.get(
        f"{self.deps.host}{endpoint}",
        headers=headers,
        params=query_params,
    )
```

### 5. create_rfq_quote

Creates a quote in response to an RFQ request.

```python
async def create_rfq_quote(
    self,
    quote: CreateRfqQuoteParams
) -> RfqQuoteResponse:
    """
    Create a quote for an RFQ request.

    The userType is automatically filled from the client's configuration.

    Args:
        quote: Quote parameters (requestId, assets, amounts)

    Returns:
        RfqQuoteResponse with quoteId
    """
    self._ensure_l2_auth()

    endpoint = "/rfq/quote"

    # Auto-fill userType
    quote_with_user_type = {
        "requestId": quote.request_id,
        "assetIn": quote.asset_in,
        "assetOut": quote.asset_out,
        "amountIn": quote.amount_in,
        "amountOut": quote.amount_out,
        "userType": self.deps.user_type,
    }

    body = json.dumps(quote_with_user_type)

    l2_header_args = L2HeaderArgs(
        method="POST",
        request_path=endpoint,
        body=body,
    )

    timestamp = await self.deps.get_server_time() if self.deps.use_server_time else None
    headers = create_l2_headers(
        self.deps.signer.address,
        self.deps.creds,
        l2_header_args,
        timestamp,
    )

    return await self.deps.post(
        f"{self.deps.host}{endpoint}",
        headers=headers,
        data=quote_with_user_type,
    )
```

### 6. get_rfq_quotes

Gets RFQ quotes with optional filtering.

```python
async def get_rfq_quotes(
    self,
    params: GetRfqQuotesParams = None
) -> RfqQuotesResponse:
    """
    Get RFQ quotes with optional filtering.

    Args:
        params: Optional filter parameters

    Returns:
        Paginated response with RFQ quotes
    """
    self._ensure_l2_auth()

    endpoint = "/rfq/data/quotes"

    l2_header_args = L2HeaderArgs(
        method="GET",
        request_path=endpoint,
    )

    timestamp = await self.deps.get_server_time() if self.deps.use_server_time else None
    headers = create_l2_headers(
        self.deps.signer.address,
        self.deps.creds,
        l2_header_args,
        timestamp,
    )

    query_params = parse_rfq_quotes_params(params)

    return await self.deps.get(
        f"{self.deps.host}{endpoint}",
        headers=headers,
        params=query_params,
    )
```

### 7. get_rfq_best_quote

Gets the best quote for a specific request.

```python
async def get_rfq_best_quote(
    self,
    params: GetRfqBestQuoteParams = None
) -> RfqQuote:
    """
    Get the best quote for an RFQ request.

    Args:
        params: Contains requestId

    Returns:
        Single RfqQuote object representing the best quote
    """
    self._ensure_l2_auth()

    endpoint = "/rfq/data/best-quote"

    l2_header_args = L2HeaderArgs(
        method="GET",
        request_path=endpoint,
    )

    timestamp = await self.deps.get_server_time() if self.deps.use_server_time else None
    headers = create_l2_headers(
        self.deps.signer.address,
        self.deps.creds,
        l2_header_args,
        timestamp,
    )

    query_params = {"requestId": params.request_id} if params else {}

    return await self.deps.get(
        f"{self.deps.host}{endpoint}",
        headers=headers,
        params=query_params,
    )
```

### 8. improve_rfq_quote

Improves an existing quote with a better amount.

```python
async def improve_rfq_quote(
    self,
    quote: ImproveRfqQuoteParams
) -> str:
    """
    Improve an existing quote with a better amountOut.

    Args:
        quote: Contains quoteId and new amountOut

    Returns:
        "OK" on success
    """
    self._ensure_l2_auth()

    endpoint = "/rfq/quote"
    body = json.dumps({
        "quoteId": quote.quote_id,
        "amountOut": quote.amount_out,
    })

    l2_header_args = L2HeaderArgs(
        method="PUT",
        request_path=endpoint,
        body=body,
    )

    timestamp = await self.deps.get_server_time() if self.deps.use_server_time else None
    headers = create_l2_headers(
        self.deps.signer.address,
        self.deps.creds,
        l2_header_args,
        timestamp,
    )

    return await self.deps.put(
        f"{self.deps.host}{endpoint}",
        headers=headers,
        data={"quoteId": quote.quote_id, "amountOut": quote.amount_out},
    )
```

### 9. cancel_rfq_quote

Cancels an existing quote.

```python
async def cancel_rfq_quote(
    self,
    quote: CancelRfqQuoteParams
) -> str:
    """
    Cancel an RFQ quote.

    Args:
        quote: Contains quoteId to cancel

    Returns:
        "OK" on success
    """
    self._ensure_l2_auth()

    endpoint = "/rfq/quote"
    body = json.dumps({"quoteId": quote.quote_id})

    l2_header_args = L2HeaderArgs(
        method="DELETE",
        request_path=endpoint,
        body=body,
    )

    timestamp = await self.deps.get_server_time() if self.deps.use_server_time else None
    headers = create_l2_headers(
        self.deps.signer.address,
        self.deps.creds,
        l2_header_args,
        timestamp,
    )

    return await self.deps.delete(
        f"{self.deps.host}{endpoint}",
        headers=headers,
        data={"quoteId": quote.quote_id},
    )
```

### 10. rfq_config

Gets the RFQ configuration from the server.

```python
async def rfq_config(self) -> Any:
    """
    Get RFQ configuration from the server.

    Returns:
        Configuration object with RFQ system parameters
    """
    self._ensure_l2_auth()

    endpoint = "/rfq/config"

    l2_header_args = L2HeaderArgs(
        method="GET",
        request_path=endpoint,
    )

    timestamp = await self.deps.get_server_time() if self.deps.use_server_time else None
    headers = create_l2_headers(
        self.deps.signer.address,
        self.deps.creds,
        l2_header_args,
        timestamp,
    )

    return await self.deps.get(
        f"{self.deps.host}{endpoint}",
        headers=headers,
    )
```

### 11. accept_rfq_quote

Accepts a quote and creates an order (taker side).

```python
async def accept_rfq_quote(
    self,
    payload: AcceptQuoteParams
) -> str:
    """
    Accept an RFQ quote (taker side).

    This method:
    1. Fetches the RFQ request details
    2. Creates a signed order based on request parameters
    3. Submits the acceptance with the order

    Args:
        payload: Contains requestId, quoteId, and expiration

    Returns:
        "OK" on success
    """
    self._ensure_l2_auth()

    # Step 1: Fetch the RFQ request
    rfq_requests = await self.get_rfq_requests(
        GetRfqRequestsParams(request_ids=[payload.request_id])
    )

    if not rfq_requests.data or len(rfq_requests.data) == 0:
        raise Exception("RFQ request not found")

    rfq_request = rfq_requests.data[0]

    # Step 2: Create an order based on request details
    side = Side.BUY if rfq_request.side == "BUY" else Side.SELL

    # Determine size based on side
    if rfq_request.side == "BUY":
        size = rfq_request.size_in
    else:
        size = rfq_request.size_out

    order = await self.deps.create_order(
        UserOrder(
            token_id=rfq_request.token,
            price=rfq_request.price,
            size=float(size),
            side=side,
            expiration=payload.expiration,
        )
    )

    if not order:
        raise Exception("Error creating order")

    # Step 3: Build accept payload
    accept_payload = {
        "requestId": payload.request_id,
        "quoteId": payload.quote_id,
        "owner": self.deps.creds.key,
        # Order fields
        "salt": int(order.salt),
        "maker": order.maker,
        "signer": order.signer,
        "taker": order.taker,
        "tokenId": order.token_id,
        "makerAmount": order.maker_amount,
        "takerAmount": order.taker_amount,
        "expiration": int(order.expiration),
        "nonce": order.nonce,
        "feeRateBps": order.fee_rate_bps,
        "side": side,
        "signatureType": order.signature_type,
        "signature": order.signature,
    }

    endpoint = "/rfq/request/accept"
    body = json.dumps(accept_payload)

    l2_header_args = L2HeaderArgs(
        method="POST",
        request_path=endpoint,
        body=body,
    )

    timestamp = await self.deps.get_server_time() if self.deps.use_server_time else None
    headers = create_l2_headers(
        self.deps.signer.address,
        self.deps.creds,
        l2_header_args,
        timestamp,
    )

    return await self.deps.post(
        f"{self.deps.host}{endpoint}",
        headers=headers,
        data=accept_payload,
    )
```

### 12. approve_rfq_order

Approves a quote and creates an order (maker side).

```python
async def approve_rfq_order(
    self,
    payload: ApproveOrderParams
) -> str:
    """
    Approve an RFQ order (maker side).

    This method:
    1. Fetches the RFQ quote details
    2. Creates a signed order based on quote parameters
    3. Submits the approval with the order

    Args:
        payload: Contains requestId, quoteId, and expiration

    Returns:
        "OK" on success
    """
    self._ensure_l2_auth()

    # Step 1: Fetch the RFQ quote
    rfq_quotes = await self.get_rfq_quotes(
        GetRfqQuotesParams(quote_ids=[payload.quote_id])
    )

    if not rfq_quotes.data or len(rfq_quotes.data) == 0:
        raise Exception("RFQ quote not found")

    rfq_quote = rfq_quotes.data[0]

    # Step 2: Create an order based on quote details
    side = Side.BUY if rfq_quote.side == "BUY" else Side.SELL

    # Determine size based on side
    if rfq_quote.side == "BUY":
        size = rfq_quote.size_in
    else:
        size = rfq_quote.size_out

    order = await self.deps.create_order(
        UserOrder(
            token_id=rfq_quote.token,
            price=rfq_quote.price,
            size=float(size),
            side=side,
            expiration=payload.expiration,
        )
    )

    if not order:
        raise Exception("Error creating order")

    # Step 3: Build approve payload
    approve_payload = {
        "requestId": payload.request_id,
        "quoteId": payload.quote_id,
        "owner": self.deps.creds.key,
        # Order fields
        "salt": int(order.salt),
        "maker": order.maker,
        "signer": order.signer,
        "taker": order.taker,
        "tokenId": order.token_id,
        "makerAmount": order.maker_amount,
        "takerAmount": order.taker_amount,
        "expiration": int(order.expiration),
        "nonce": order.nonce,
        "feeRateBps": order.fee_rate_bps,
        "side": side,
        "signatureType": order.signature_type,
        "signature": order.signature,
    }

    endpoint = "/rfq/quote/approve"
    body = json.dumps(approve_payload)

    l2_header_args = L2HeaderArgs(
        method="POST",
        request_path=endpoint,
        body=body,
    )

    timestamp = await self.deps.get_server_time() if self.deps.use_server_time else None
    headers = create_l2_headers(
        self.deps.signer.address,
        self.deps.creds,
        l2_header_args,
        timestamp,
    )

    return await self.deps.post(
        f"{self.deps.host}{endpoint}",
        headers=headers,
        data=approve_payload,
    )
```

### Helper: _ensure_l2_auth

```python
def _ensure_l2_auth(self):
    """
    Verify that L2 authentication is available.

    Raises:
        Exception if signer or creds are not configured
    """
    if self.deps.signer is None:
        raise Exception("L1 auth unavailable: signer is required")

    if self.deps.creds is None:
        raise Exception("L2 auth not available: API credentials are required")
```

---

## Utility Functions

### Rounding Functions

```python
def decimal_places(num: float) -> int:
    """Count decimal places in a number."""
    if num == int(num):
        return 0

    str_num = str(num)
    if '.' not in str_num:
        return 0

    return len(str_num.split('.')[1])


def round_normal(num: float, decimals: int) -> float:
    """
    Round to nearest value with specified decimal places.
    Standard rounding (0.5 rounds up).
    """
    if decimal_places(num) <= decimals:
        return num

    multiplier = 10 ** decimals
    return round(num * multiplier) / multiplier


def round_down(num: float, decimals: int) -> float:
    """
    Round down (floor) to specified decimal places.
    """
    if decimal_places(num) <= decimals:
        return num

    import math
    multiplier = 10 ** decimals
    return math.floor(num * multiplier) / multiplier


def round_up(num: float, decimals: int) -> float:
    """
    Round up (ceiling) to specified decimal places.
    """
    if decimal_places(num) <= decimals:
        return num

    import math
    multiplier = 10 ** decimals
    return math.ceil(num * multiplier) / multiplier
```

### Parse Units

```python
def parse_units(value: str, decimals: int) -> int:
    """
    Convert a decimal string to smallest units (like wei).

    Args:
        value: Decimal string (e.g., "1.5")
        decimals: Number of decimal places (e.g., 6 for USDC)

    Returns:
        Integer in smallest units (e.g., 1500000 for "1.5" with 6 decimals)
    """
    # Handle the decimal conversion
    if '.' in value:
        integer_part, decimal_part = value.split('.')
        # Pad or truncate decimal part to match decimals
        decimal_part = decimal_part[:decimals].ljust(decimals, '0')
        return int(integer_part + decimal_part)
    else:
        return int(value) * (10 ** decimals)
```

### Query Parameter Parsing

```python
def parse_rfq_requests_params(params: GetRfqRequestsParams = None) -> dict:
    """
    Convert GetRfqRequestsParams to query string parameters.
    Arrays are converted to comma-separated strings.
    """
    if params is None:
        return {}

    result = {}

    # Copy non-array fields directly
    for field in ['userAddress', 'state', 'sizeMin', 'sizeMax',
                  'sizeUsdcMin', 'sizeUsdcMax', 'priceMin', 'priceMax',
                  'sortBy', 'sortDir', 'limit', 'offset']:
        value = getattr(params, to_snake_case(field), None)
        if value is not None:
            result[field] = value

    # Convert arrays to comma-separated strings
    if params.request_ids:
        result['requestIds'] = ','.join(params.request_ids)
    if params.states:
        result['states'] = ','.join(params.states)
    if params.markets:
        result['markets'] = ','.join(params.markets)

    return result


def parse_rfq_quotes_params(params: GetRfqQuotesParams = None) -> dict:
    """
    Convert GetRfqQuotesParams to query string parameters.
    Arrays are converted to comma-separated strings.
    """
    if params is None:
        return {}

    result = {}

    # Copy non-array fields directly
    for field in ['userAddress', 'state', 'sizeMin', 'sizeMax',
                  'sizeUsdcMin', 'sizeUsdcMax', 'priceMin', 'priceMax',
                  'sortBy', 'sortDir', 'limit', 'offset']:
        value = getattr(params, to_snake_case(field), None)
        if value is not None:
            result[field] = value

    # Convert arrays to comma-separated strings
    if params.quote_ids:
        result['quoteIds'] = ','.join(params.quote_ids)
    if params.request_ids:
        result['requestIds'] = ','.join(params.request_ids)
    if params.states:
        result['states'] = ','.join(params.states)
    if params.markets:
        result['markets'] = ','.join(params.markets)

    return result
```

---

## Complete Flow Examples

### Example 1: Taker Creates and Manages a Request

```python
# Initialize client (assuming clob_client is already set up)
rfq = clob_client.rfq

# Step 1: Create RFQ request parameters
# Buy 40 YES tokens at $0.50 each = $20 total
token_id = "34097058504275310827233323421517291090691602969494795225921954353603704046623"

request_params = await rfq.create_rfq_request(
    RfqUserOrder(
        token_id=token_id,
        price=0.5,
        side=Side.BUY,
        size=40,
    ),
    CreateOrderOptions(tick_size="0.01"),
)

# Result:
# CreateRfqRequestParams(
#     asset_in="34097058504275310827233323421517291090691602969494795225921954353603704046623",
#     asset_out="0",
#     amount_in="40000000",   # 40 tokens (6 decimals)
#     amount_out="20000000",  # $20 USDC (6 decimals)
#     user_type=0
# )

# Step 2: Post the request
response = await rfq.post_rfq_request(request_params)
request_id = response.request_id
print(f"Created request: {request_id}")

# Step 3: Check for quotes
quotes = await rfq.get_rfq_quotes(
    GetRfqQuotesParams(request_ids=[request_id])
)
print(f"Found {len(quotes.data)} quotes")

# Step 4: Accept a quote
if quotes.data:
    best_quote = quotes.data[0]
    result = await rfq.accept_rfq_quote(
        AcceptQuoteParams(
            request_id=request_id,
            quote_id=best_quote.quote_id,
            expiration=int(time.time()) + 3600,  # 1 hour
        )
    )
    print(f"Accepted quote: {result}")

# Alternative: Cancel the request
# result = await rfq.cancel_rfq_request(
#     CancelRfqRequestParams(request_id=request_id)
# )
```

### Example 2: Maker Provides Quotes

```python
rfq = clob_client.rfq

# Step 1: Find active requests
requests = await rfq.get_rfq_requests(
    GetRfqRequestsParams(
        state="active",
        limit=10,
    )
)

# Step 2: Quote on an interesting request
if requests.data:
    request = requests.data[0]

    # If request is BUY: requester wants tokens, will pay USDC
    # Maker provides USDC (assetIn), receives tokens (assetOut)
    if request.side == "BUY":
        quote_response = await rfq.create_rfq_quote(
            CreateRfqQuoteParams(
                request_id=request.request_id,
                asset_in="0",  # Maker pays USDC
                asset_out=request.token,  # Maker receives tokens
                amount_in=request.size_out,  # Same USDC amount
                amount_out=request.size_in,  # Same token amount
            )
        )
    else:
        # Request is SELL: requester wants to sell tokens for USDC
        quote_response = await rfq.create_rfq_quote(
            CreateRfqQuoteParams(
                request_id=request.request_id,
                asset_in=request.token,  # Maker pays tokens
                asset_out="0",  # Maker receives USDC
                amount_in=request.size_out,
                amount_out=request.size_in,
            )
        )

    print(f"Created quote: {quote_response.quote_id}")

# Step 3: Improve quote if needed
await rfq.improve_rfq_quote(
    ImproveRfqQuoteParams(
        quote_id=quote_response.quote_id,
        amount_out="40500000",  # Better amount
    )
)

# Step 4: When quote is accepted, approve the order
result = await rfq.approve_rfq_order(
    ApproveOrderParams(
        request_id=request.request_id,
        quote_id=quote_response.quote_id,
        expiration=int(time.time()) + 3600,
    )
)
print(f"Approved order: {result}")
```

### Example 3: Getting Best Quote

```python
rfq = clob_client.rfq

request_id = "019a83a9-f4c7-7c96-9139-2da2b2d934ef"

best_quote = await rfq.get_rfq_best_quote(
    GetRfqBestQuoteParams(request_id=request_id)
)

print(f"Best quote: {best_quote.quote_id}")
print(f"Price: {best_quote.price}")
print(f"Size In: {best_quote.size_in}")
print(f"Size Out: {best_quote.size_out}")
```

---

## Error Handling

### Common Errors

```python
class RfqErrors:
    L1_AUTH_UNAVAILABLE = "L1 auth unavailable: signer is required"
    L2_AUTH_NOT_AVAILABLE = "L2 auth not available: API credentials are required"
    RFQ_REQUEST_NOT_FOUND = "RFQ request not found"
    RFQ_QUOTE_NOT_FOUND = "RFQ quote not found"
    ORDER_CREATION_ERROR = "Error creating order"
```

### HTTP Error Response Format

When an API request fails, the response may include:

```python
{
    "error": "Error message",
    "status": 400  # HTTP status code
}
```

---

## JSON Serialization Notes

When sending requests to the API, use camelCase for field names:

| Python (snake_case) | JSON (camelCase) |
|---------------------|------------------|
| `request_id` | `requestId` |
| `quote_id` | `quoteId` |
| `asset_in` | `assetIn` |
| `asset_out` | `assetOut` |
| `amount_in` | `amountIn` |
| `amount_out` | `amountOut` |
| `user_type` | `userType` |
| `user_address` | `userAddress` |
| `size_min` | `sizeMin` |
| `size_max` | `sizeMax` |
| `price_min` | `priceMin` |
| `price_max` | `priceMax` |
| `sort_by` | `sortBy` |
| `sort_dir` | `sortDir` |

---

## Summary

This specification covers the complete RFQ client implementation including:

1. **Authentication**: L2 HMAC-based authentication with API keys
2. **Data Types**: All input and output types for RFQ operations
3. **Endpoints**: Complete list of API endpoints
4. **Methods**: Detailed implementation of all 12 RFQ methods
5. **Utilities**: Rounding, parsing, and helper functions
6. **Examples**: Complete flow examples for takers and makers

When implementing in Python (or another language), ensure:
- Proper HMAC signature generation with URL-safe base64 encoding
- Correct decimal handling for amounts (6 decimal places)
- Proper rounding based on tick size configuration
- camelCase JSON serialization for API requests
