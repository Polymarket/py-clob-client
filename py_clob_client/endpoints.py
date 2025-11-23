# The following constants define the API endpoints for the trading platform,
# categorized by their primary function for improved readability and maintenance.

# =============================================================================
# 1. GENERAL UTILITY & TIME ENDPOINTS
# =============================================================================

# Endpoint for checking server latency and retrieving the current server time.
TIME = "/time"


# =============================================================================
# 2. AUTHENTICATION & API KEY MANAGEMENT
# =============================================================================

# Endpoint to create a new API key pair.
CREATE_API_KEY = "/auth/api-key"

# Endpoint to fetch a list of existing API keys for the user.
GET_API_KEYS = "/auth/api-keys"

# Endpoint to delete or revoke an existing API key.
DELETE_API_KEY = "/auth/api-key"

# Endpoint for deriving a new key from an existing one (e.g., for permissions scoping).
DERIVE_API_KEY = "/auth/derive-api-key"

# Endpoint to check the ban status, specifically for 'closed-only' accounts.
CLOSED_ONLY = "/auth/ban-status/closed-only"


# =============================================================================
# 3. MARKET DATA (READ-ONLY) ENDPOINTS
# =============================================================================
# These endpoints provide real-time and historical information on markets.
# 

# Endpoint to retrieve recent trade data for a market or markets.
TRADES = "/data/trades"

# Endpoint to get the current order book snapshot for a single market.
GET_ORDER_BOOK = "/book"

# Endpoint to get order book snapshots for multiple markets in a single request.
GET_ORDER_BOOKS = "/books"

# Endpoint to retrieve the midpoint price (average of best bid and ask).
MID_POINT = "/midpoint"

# Endpoint to retrieve midpoint prices for multiple markets.
MID_POINTS = "/midpoints"

# Endpoint to retrieve the latest price for a single market.
PRICE = "/price"

# Endpoint to retrieve the latest prices for multiple markets.
GET_PRICES = "/prices"

# Endpoint to retrieve the current spread (difference between best bid and ask).
GET_SPREAD = "/spread"

# Endpoint to retrieve spreads for multiple markets.
GET_SPREADS = "/spreads"

# Endpoint to get the price of the most recent trade for a single market.
GET_LAST_TRADE_PRICE = "/last-trade-price"

# Endpoint to get the last trade prices for multiple markets.
GET_LAST_TRADES_PRICES = "/last-trades-prices"

# Endpoint to fetch the tick size (minimum price fluctuation) for a market.
GET_TICK_SIZE = "/tick-size"

# Endpoint to retrieve trade events for a specific market (live feed).
GET_MARKET_TRADES_EVENTS = "/live-activity/events/"

# Endpoint to fetch trades made by a specific "builder" entity (often related to liquidity provision).
GET_BUILDER_TRADES = "/builder/trades"


# =============================================================================
# 4. ORDER MANAGEMENT (TRADING) ENDPOINTS
# =============================================================================

# Endpoint to retrieve detailed information about a specific single order.
GET_ORDER = "/data/order/"

# Endpoint to retrieve all active or recent orders for the user.
ORDERS = "/data/orders"

# Endpoint to submit a single new order (Limit, Market, etc.).
POST_ORDER = "/order"

# Endpoint to submit multiple new orders in a batch request (batch order submission).
POST_ORDERS = "/orders"

# Endpoint to cancel a single open order.
CANCEL = "/order"

# Endpoint to cancel multiple specific orders in a batch request.
CANCEL_ORDERS = "/orders"

# Endpoint to cancel all open orders across all markets for the user.
CANCEL_ALL = "/cancel-all"

# Endpoint to cancel all active market orders (potentially used to clear pending market orders).
CANCEL_MARKET_ORDERS = "/cancel-market-orders"


# =============================================================================
# 5. ACCOUNT, FEES, & METADATA ENDPOINTS
# =============================================================================

# Endpoint to fetch user notifications (e.g., maintenance, important updates).
GET_NOTIFICATIONS = "/notifications"

# Endpoint to acknowledge and clear notifications.
DROP_NOTIFICATIONS = "/notifications"

# Endpoint to check the current balance and available trading allowance (e.g., for margin/leverage).
GET_BALANCE_ALLOWANCE = "/balance-allowance"

# Endpoint to update the user's trading allowance/settings.
UPDATE_BALANCE_ALLOWANCE = "/balance-allowance/update"

# Endpoint to check if a single order is eligible for scoring (e.g., fee tier determination).
IS_ORDER_SCORING = "/order-scoring"

# Endpoint to check if multiple orders are eligible for scoring.
ARE_ORDERS_SCORING = "/orders-scoring"

# Endpoint to retrieve negative risk exposure details.
GET_NEG_RISK = "/neg-risk"

# Endpoint to retrieve the current trading fee rate applied to the user.
GET_FEE_RATE = "/fee-rate"

# Endpoint to fetch simplified market data structures (potentially less verbose).
GET_SAMPLING_SIMPLIFIED_MARKETS = "/sampling-simplified-markets"

# Endpoint to fetch sampled market data for all markets.
GET_SAMPLING_MARKETS = "/sampling-markets"

# Endpoint to fetch simplified market data structures for all markets.
GET_SIMPLIFIED_MARKETS = "/simplified-markets"

# Endpoint to fetch detailed metadata for all available trading markets.
GET_MARKETS = "/markets"

# Endpoint to fetch detailed metadata for a specific market by ID.
GET_MARKET = "/markets/"
