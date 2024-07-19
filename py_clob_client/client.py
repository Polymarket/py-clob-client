import logging
from typing import Optional

from .order_builder.builder import OrderBuilder
from .headers.headers import create_level_1_headers, create_level_2_headers
from .signer import Signer
from .config import get_contract_config

from .endpoints import (
    CANCEL,
    CANCEL_ORDERS,
    CANCEL_MARKET_ORDERS,
    CANCEL_ALL,
    CREATE_API_KEY,
    DELETE_API_KEY,
    DERIVE_API_KEY,
    GET_API_KEYS,
    GET_LAST_TRADE_PRICE,
    GET_ORDER,
    GET_ORDER_BOOK,
    MID_POINT,
    ORDERS,
    POST_ORDER,
    PRICE,
    TIME,
    TRADES,
    GET_NOTIFICATIONS,
    DROP_NOTIFICATIONS,
    GET_BALANCE_ALLOWANCE,
    UPDATE_BALANCE_ALLOWANCE,
    IS_ORDER_SCORING,
    GET_TICK_SIZE,
    GET_NEG_RISK,
    ARE_ORDERS_SCORING,
    GET_SIMPLIFIED_MARKETS,
    GET_MARKETS,
    GET_MARKET,
    GET_SAMPLING_SIMPLIFIED_MARKETS,
    GET_SAMPLING_MARKETS,
    GET_MARKET_TRADES_EVENTS,
    GET_LAST_TRADES_PRICES,
    MID_POINTS,
    GET_ORDER_BOOKS,
    GET_PRICES,
    GET_SPREAD,
    GET_SPREADS,
)
from .clob_types import (
    ApiCreds,
    TradeParams,
    OpenOrderParams,
    OrderArgs,
    RequestArgs,
    DropNotificationParams,
    OrderBookSummary,
    BalanceAllowanceParams,
    OrderScoringParams,
    TickSize,
    CreateOrderOptions,
    OrdersScoringParams,
    OrderType,
    PartialCreateOrderOptions,
    BookParams,
    MarketOrderArgs,
)
from .exceptions import PolyException
from .http_helpers.helpers import (
    add_query_trade_params,
    add_query_open_orders_params,
    delete,
    get,
    post,
    drop_notifications_query_params,
    add_balance_allowance_params_to_url,
    add_order_scoring_params_to_url,
)

from .constants import L0, L1, L1_AUTH_UNAVAILABLE, L2, L2_AUTH_UNAVAILABLE, END_CURSOR
from .utilities import (
    parse_raw_orderbook_summary,
    generate_orderbook_summary_hash,
    order_to_json,
    is_tick_size_smaller,
    price_valid,
)


class ClobClient:
    def __init__(
        self,
        host,
        chain_id: int = None,
        key: str = None,
        creds: ApiCreds = None,
        signature_type: int = None,
        funder: str = None,
    ):
        """
        Initializes the clob client
        The client can be started in 3 modes:
        1) Level 0: Requires only the clob host url
                    Allows access to open CLOB endpoints

        2) Level 1: Requires the host, chain_id and a private key.
                    Allows access to L1 authenticated endpoints + all unauthenticated endpoints

        3) Level 2: Requires the host, chain_id, a private key, and Credentials.
                    Allows access to all endpoints
        """
        self.host = host[0:-1] if host.endswith("/") else host
        self.chain_id = chain_id
        self.signer = Signer(key, chain_id) if key else None
        self.creds = creds
        self.mode = self._get_client_mode()

        if self.signer:
            self.builder = OrderBuilder(
                self.signer, sig_type=signature_type, funder=funder
            )

        # local cache
        self.__tick_sizes = {}
        self.__neg_risk = {}

        self.logger = logging.getLogger(self.__class__.__name__)

    def get_address(self):
        """
        Returns the public address of the signer
        """
        return self.signer.address() if self.signer else None

    def get_collateral_address(self):
        """
        Returns the collateral token address
        """
        contract_config = get_contract_config(self.chain_id)
        if contract_config:
            return contract_config.collateral

    def get_conditional_address(self):
        """
        Returns the conditional token address
        """
        contract_config = get_contract_config(self.chain_id)
        if contract_config:
            return contract_config.conditional_tokens

    def get_exchange_address(self, neg_risk=False):
        """
        Returns the exchange address
        """
        contract_config = get_contract_config(self.chain_id, neg_risk)
        if contract_config:
            return contract_config.exchange

    def get_ok(self):
        """
        Health check: Confirms that the server is up
        Does not need authentication
        """
        return get("{}/".format(self.host))

    def get_server_time(self):
        """
        Returns the current timestamp on the server
        Does not need authentication
        """
        return get("{}{}".format(self.host, TIME))

    def create_api_key(self, nonce: int = None) -> ApiCreds:
        """
        Creates a new CLOB API key for the given
        """
        self.assert_level_1_auth()

        endpoint = "{}{}".format(self.host, CREATE_API_KEY)
        headers = create_level_1_headers(self.signer, nonce)

        creds_raw = post(endpoint, headers=headers)
        try:
            creds = ApiCreds(
                api_key=creds_raw["apiKey"],
                api_secret=creds_raw["secret"],
                api_passphrase=creds_raw["passphrase"],
            )
        except:
            self.logger.error("Couldn't parse created CLOB creds")
            return None
        return creds

    def derive_api_key(self, nonce: int = None) -> ApiCreds:
        """
        Derives an already existing CLOB API key for the given address and nonce
        """
        self.assert_level_1_auth()

        endpoint = "{}{}".format(self.host, DERIVE_API_KEY)
        headers = create_level_1_headers(self.signer, nonce)

        creds_raw = get(endpoint, headers=headers)
        try:
            creds = ApiCreds(
                api_key=creds_raw["apiKey"],
                api_secret=creds_raw["secret"],
                api_passphrase=creds_raw["passphrase"],
            )
        except:
            self.logger.error("Couldn't parse derived CLOB creds")
            return None
        return creds

    def create_or_derive_api_creds(self, nonce: int = None) -> ApiCreds:
        """
        Creates API creds if not already created for nonce, otherwise derives them
        """
        try:
            return self.create_api_key(nonce)
        except:
            return self.derive_api_key(nonce)

    def set_api_creds(self, creds: ApiCreds):
        """
        Sets client api creds
        """
        self.creds = creds
        self.mode = self._get_client_mode()

    def get_api_keys(self):
        """
        Gets the available API keys for this address
        Level 2 Auth required
        """
        self.assert_level_2_auth()

        request_args = RequestArgs(method="GET", request_path=GET_API_KEYS)
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        return get("{}{}".format(self.host, GET_API_KEYS), headers=headers)

    def delete_api_key(self):
        """
        Deletes an API key
        Level 2 Auth required
        """
        self.assert_level_2_auth()

        request_args = RequestArgs(method="DELETE", request_path=DELETE_API_KEY)
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        return delete("{}{}".format(self.host, DELETE_API_KEY), headers=headers)

    def get_midpoint(self, token_id):
        """
        Get the mid market price for the given market
        """
        return get("{}{}?token_id={}".format(self.host, MID_POINT, token_id))

    def get_midpoints(self, params: list[BookParams]):
        """
        Get the mid market prices for a set of token ids
        """
        body = [{"token_id": param.token_id} for param in params]
        return post("{}{}".format(self.host, MID_POINTS), data=body)

    def get_price(self, token_id, side):
        """
        Get the market price for the given market
        """
        return get("{}{}?token_id={}&side={}".format(self.host, PRICE, token_id, side))

    def get_prices(self, params: list[BookParams]):
        """
        Get the market prices for a set
        """
        body = [{"token_id": param.token_id, "side": param.side} for param in params]
        return post("{}{}".format(self.host, GET_PRICES), data=body)

    def get_spread(self, token_id):
        """
        Get the spread for the given market
        """
        return get("{}{}?token_id={}".format(self.host, GET_SPREAD, token_id))

    def get_spreads(self, params: list[BookParams]):
        """
        Get the spreads for a set of token ids
        """
        body = [{"token_id": param.token_id} for param in params]
        return post("{}{}".format(self.host, GET_SPREADS), data=body)

    def get_tick_size(self, token_id: str) -> TickSize:
        if token_id in self.__tick_sizes:
            return self.__tick_sizes[token_id]

        result = get("{}{}?token_id={}".format(self.host, GET_TICK_SIZE, token_id))
        self.__tick_sizes[token_id] = str(result["minimum_tick_size"])

        return self.__tick_sizes[token_id]

    def get_neg_risk(self, token_id: str) -> bool:
        if token_id in self.__neg_risk:
            return self.__neg_risk[token_id]

        result = get("{}{}?token_id={}".format(self.host, GET_NEG_RISK, token_id))
        self.__neg_risk[token_id] = result["neg_risk"]

        return result["neg_risk"]

    def __resolve_tick_size(
        self, token_id: str, tick_size: TickSize = None
    ) -> TickSize:
        min_tick_size = self.get_tick_size(token_id)
        if tick_size is not None:
            if is_tick_size_smaller(tick_size, min_tick_size):
                raise Exception(
                    "invalid tick size ("
                    + str(tick_size)
                    + "), minimum for the market is "
                    + str(min_tick_size),
                )
        else:
            tick_size = min_tick_size
        return tick_size

    def create_order(
        self, order_args: OrderArgs, options: Optional[PartialCreateOrderOptions] = None
    ):
        """
        Creates and signs an order
        Level 1 Auth required
        """
        self.assert_level_1_auth()

        # add resolve_order_options, or similar
        tick_size = self.__resolve_tick_size(
            order_args.token_id,
            options.tick_size if options else None,
        )

        if not price_valid(order_args.price, tick_size):
            raise Exception(
                "price ("
                + str(order_args.price)
                + "), min: "
                + str(tick_size)
                + " - max: "
                + str(1 - float(tick_size))
            )

        neg_risk = (
            options.neg_risk
            if options and options.neg_risk
            else self.get_neg_risk(order_args.token_id)
        )

        return self.builder.create_order(
            order_args,
            CreateOrderOptions(
                tick_size=tick_size,
                neg_risk=neg_risk,
            ),
        )

    def create_market_order(
        self,
        order_args: MarketOrderArgs,
        options: Optional[PartialCreateOrderOptions] = None,
    ):
        """
        Creates and signs an order
        Level 1 Auth required
        """
        self.assert_level_1_auth()

        # add resolve_order_options, or similar
        tick_size = self.__resolve_tick_size(
            order_args.token_id,
            options.tick_size if options else None,
        )

        if order_args.price is None or order_args.price <= 0:
            order_args.price = self.calculate_market_price(
                order_args.token_id, "BUY", order_args.amount
            )

        if not price_valid(order_args.price, tick_size):
            raise Exception(
                "price ("
                + str(order_args.price)
                + "), min: "
                + str(tick_size)
                + " - max: "
                + str(1 - float(tick_size))
            )

        neg_risk = (
            options.neg_risk
            if options and options.neg_risk
            else self.get_neg_risk(order_args.token_id)
        )

        return self.builder.create_market_order(
            order_args,
            CreateOrderOptions(
                tick_size=tick_size,
                neg_risk=neg_risk,
            ),
        )

    def post_order(self, order, orderType: OrderType = OrderType.GTC):
        """
        Posts the order
        """
        self.assert_level_2_auth()
        body = order_to_json(order, self.creds.api_key, orderType)
        headers = create_level_2_headers(
            self.signer,
            self.creds,
            RequestArgs(method="POST", request_path=POST_ORDER, body=body),
        )
        return post("{}{}".format(self.host, POST_ORDER), headers=headers, data=body)

    def create_and_post_order(
        self, order_args: OrderArgs, options: PartialCreateOrderOptions = None
    ):
        """
        Utility function to create and publish an order
        """
        ord = self.create_order(order_args, options)
        return self.post_order(ord)

    def cancel(self, order_id):
        """
        Cancels an order
        Level 2 Auth required
        """
        self.assert_level_2_auth()
        body = {"orderID": order_id}

        request_args = RequestArgs(method="DELETE", request_path=CANCEL, body=body)
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        return delete("{}{}".format(self.host, CANCEL), headers=headers, data=body)

    def cancel_orders(self, order_ids):
        """
        Cancels orders
        Level 2 Auth required
        """
        self.assert_level_2_auth()
        body = order_ids

        request_args = RequestArgs(
            method="DELETE", request_path=CANCEL_ORDERS, body=body
        )
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        return delete(
            "{}{}".format(self.host, CANCEL_ORDERS), headers=headers, data=body
        )

    def cancel_all(self):
        """
        Cancels all available orders for the user
        Level 2 Auth required
        """
        self.assert_level_2_auth()
        request_args = RequestArgs(method="DELETE", request_path=CANCEL_ALL)
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        return delete("{}{}".format(self.host, CANCEL_ALL), headers=headers)

    def cancel_market_orders(self, market: str = "", asset_id: str = ""):
        """
        Cancels orders
        Level 2 Auth required
        """
        self.assert_level_2_auth()
        body = {"market": market, "asset_id": asset_id}

        request_args = RequestArgs(
            method="DELETE", request_path=CANCEL_MARKET_ORDERS, body=body
        )
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        return delete(
            "{}{}".format(self.host, CANCEL_MARKET_ORDERS), headers=headers, data=body
        )

    def get_orders(self, params: OpenOrderParams = None, next_cursor="MA=="):
        """
        Gets orders for the API key
        Requires Level 2 authentication
        """
        self.assert_level_2_auth()
        request_args = RequestArgs(method="GET", request_path=ORDERS)
        headers = create_level_2_headers(self.signer, self.creds, request_args)

        results = []
        next_cursor = next_cursor if next_cursor is not None else "MA=="
        while next_cursor != END_CURSOR:
            url = add_query_open_orders_params(
                "{}{}".format(self.host, ORDERS), params, next_cursor
            )
            response = get(url, headers=headers)
            next_cursor = response["next_cursor"]
            results += response["data"]

        return results

    def get_order_book(self, token_id) -> OrderBookSummary:
        """
        Fetches the orderbook for the token_id
        """
        raw_obs = get("{}{}?token_id={}".format(self.host, GET_ORDER_BOOK, token_id))
        return parse_raw_orderbook_summary(raw_obs)

    def get_order_books(self, params: list[BookParams]) -> list[OrderBookSummary]:
        """
        Fetches the orderbook for a set of token ids
        """
        body = [{"token_id": param.token_id} for param in params]
        raw_obs = post("{}{}".format(self.host, GET_ORDER_BOOKS), data=body)
        return [parse_raw_orderbook_summary(r) for r in raw_obs]

    def get_order_book_hash(self, orderbook: OrderBookSummary) -> str:
        """
        Calculates the hash for the given orderbook
        """
        return generate_orderbook_summary_hash(orderbook)

    def get_order(self, order_id):
        """
        Fetches the order corresponding to the order_id
        Requires Level 2 authentication
        """
        self.assert_level_2_auth()
        endpoint = "{}{}".format(GET_ORDER, order_id)
        request_args = RequestArgs(method="GET", request_path=endpoint)
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        return get("{}{}".format(self.host, endpoint), headers=headers)

    def get_trades(self, params: TradeParams = None, next_cursor="MA=="):
        """
        Fetches the trade history for a user
        Requires Level 2 authentication
        """
        self.assert_level_2_auth()
        request_args = RequestArgs(method="GET", request_path=TRADES)
        headers = create_level_2_headers(self.signer, self.creds, request_args)

        results = []
        next_cursor = next_cursor if next_cursor is not None else "MA=="
        while next_cursor != END_CURSOR:
            url = add_query_trade_params(
                "{}{}".format(self.host, TRADES), params, next_cursor
            )
            response = get(url, headers=headers)
            next_cursor = response["next_cursor"]
            results += response["data"]

        return results

    def get_last_trade_price(self, token_id):
        """
        Fetches the last trade price token_id
        """
        return get("{}{}?token_id={}".format(self.host, GET_LAST_TRADE_PRICE, token_id))

    def get_last_trades_prices(self, params: list[BookParams]):
        """
        Fetches the last trades prices for a set of token ids
        """
        body = [{"token_id": param.token_id} for param in params]
        return post("{}{}".format(self.host, GET_LAST_TRADES_PRICES), data=body)

    def assert_level_1_auth(self):
        """
        Level 1 Poly Auth
        """
        if self.mode < L1:
            raise PolyException(L1_AUTH_UNAVAILABLE)

    def assert_level_2_auth(self):
        """
        Level 2 Poly Auth
        """
        if self.mode < L2:
            raise PolyException(L2_AUTH_UNAVAILABLE)

    def _get_client_mode(self):
        if self.signer is not None and self.creds is not None:
            return L2
        if self.signer is not None:
            return L1
        return L0

    def get_notifications(self):
        """
        Fetches the notifications for a user
        Requires Level 2 authentication
        """
        self.assert_level_2_auth()
        request_args = RequestArgs(method="GET", request_path=GET_NOTIFICATIONS)
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        url = "{}{}?signature_type={}".format(
            self.host, GET_NOTIFICATIONS, self.builder.sig_type
        )
        return get(url, headers=headers)

    def drop_notifications(self, params: DropNotificationParams = None):
        """
        Drops the notifications for a user
        Requires Level 2 authentication
        """
        self.assert_level_2_auth()
        request_args = RequestArgs(method="DELETE", request_path=DROP_NOTIFICATIONS)
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        url = drop_notifications_query_params(
            "{}{}".format(self.host, DROP_NOTIFICATIONS), params
        )
        return delete(url, headers=headers)

    def get_balance_allowance(self, params: BalanceAllowanceParams = None):
        """
        Fetches the balance & allowance for a user
        Requires Level 2 authentication
        """
        self.assert_level_2_auth()
        request_args = RequestArgs(method="GET", request_path=GET_BALANCE_ALLOWANCE)
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        if params.signature_type == -1:
            params.signature_type = self.builder.sig_type
        url = add_balance_allowance_params_to_url(
            "{}{}".format(self.host, GET_BALANCE_ALLOWANCE), params
        )
        return get(url, headers=headers)

    def update_balance_allowance(self, params: BalanceAllowanceParams = None):
        """
        Updates the balance & allowance for a user
        Requires Level 2 authentication
        """
        self.assert_level_2_auth()
        request_args = RequestArgs(method="GET", request_path=UPDATE_BALANCE_ALLOWANCE)
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        if params.signature_type == -1:
            params.signature_type = self.builder.sig_type
        url = add_balance_allowance_params_to_url(
            "{}{}".format(self.host, UPDATE_BALANCE_ALLOWANCE), params
        )
        return get(url, headers=headers)

    def is_order_scoring(self, params: OrderScoringParams):
        """
        Check if the order is currently scoring
        Requires Level 2 authentication
        """
        self.assert_level_2_auth()
        request_args = RequestArgs(method="GET", request_path=IS_ORDER_SCORING)
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        url = add_order_scoring_params_to_url(
            "{}{}".format(self.host, IS_ORDER_SCORING), params
        )
        return get(url, headers=headers)

    def are_orders_scoring(self, params: OrdersScoringParams):
        """
        Check if the orders are currently scoring
        Requires Level 2 authentication
        """
        self.assert_level_2_auth()
        body = params.orderIds
        request_args = RequestArgs(
            method="POST", request_path=ARE_ORDERS_SCORING, body=body
        )
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        return post(
            "{}{}".format(self.host, ARE_ORDERS_SCORING), headers=headers, data=body
        )

    def get_sampling_markets(self, next_cursor="MA=="):
        """
        Get the current sampling markets
        """
        return get(
            "{}{}?next_cursor={}".format(self.host, GET_SAMPLING_MARKETS, next_cursor)
        )

    def get_sampling_simplified_markets(self, next_cursor="MA=="):
        """
        Get the current sampling simplified markets
        """
        return get(
            "{}{}?next_cursor={}".format(
                self.host, GET_SAMPLING_SIMPLIFIED_MARKETS, next_cursor
            )
        )

    def get_markets(self, next_cursor="MA=="):
        """
        Get the current markets
        """
        return get("{}{}?next_cursor={}".format(self.host, GET_MARKETS, next_cursor))

    def get_simplified_markets(self, next_cursor="MA=="):
        """
        Get the current simplified markets
        """
        return get(
            "{}{}?next_cursor={}".format(self.host, GET_SIMPLIFIED_MARKETS, next_cursor)
        )

    def get_market(self, condition_id):
        """
        Get a market by condition_id
        """
        return get("{}{}{}".format(self.host, GET_MARKET, condition_id))

    def get_market_trades_events(self, condition_id):
        """
        Get the market's trades events by condition id
        """
        return get("{}{}{}".format(self.host, GET_MARKET_TRADES_EVENTS, condition_id))

    def calculate_market_price(self, token_id: str, side: str, amount: float) -> float:
        """
        Calculates the matching price considering an amount and the current orderbook
        """
        book = self.get_order_book(token_id)
        if book is None:
            raise Exception("no orderbook")
        if side == "BUY":
            if book.asks is None:
                raise Exception("no match")
            return self.builder.calculate_market_price(book.asks, amount)
        else:
            if book.bids is None:
                raise Exception("no match")
            return self.builder.calculate_market_price(book.bids, amount)
