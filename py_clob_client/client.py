import logging

from .orders.builder import OrderBuilder

from .headers import create_level_1_headers, create_level_2_headers
from .signer import Signer

from .endpoints import CANCEL, CANCEL_ALL, CREATE_API_KEY, DELETE_API_KEY, DERIVE_API_KEY, GET_API_KEYS, GET_ORDER, GET_ORDER_BOOK, MID_POINT, OPEN_ORDERS, ORDER_HISTORY, POST_ORDER, PRICE, TIME, TRADE_HISTORY
from .clob_types import ApiCreds, FilterParams, LimitOrderArgs, MarketOrderArgs, RequestArgs
from .exceptions import PolyException
from .http_helpers.helpers import add_query_params, delete, get, post
from py_order_utils.config import get_contract_config
from .constants import L0, L1, L1_AUTH_UNAVAILABLE, L2, L2_AUTH_UNAVAILABLE


class ClobClient:
    def __init__(self, host, chain_id: int = None, key:str = None, creds:ApiCreds = None, signature_type: int = None, funder: str = None):
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
        self.host = host
        self.signer = Signer(key, chain_id) if key else None
        self.creds = creds
        self.mode = self._get_client_mode()
        if chain_id:
            self.contract_config = get_contract_config(chain_id)
        if self.signer:
            self.builder = OrderBuilder(self.signer, sig_type=signature_type, funder=funder)
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_address(self):
        """
        Returns the public address of the signer
        """
        return self.signer.address if self.signer else None

    def get_collateral_address(self):
        """
        Returns the collateral token address
        """
        if self.contract_config:
            return self.contract_config.get_collateral()

    def get_conditional_address(self):
        """
        Returns the conditional token address
        """
        if self.contract_config:
            return self.contract_config.get_conditional()

    def get_exchange_address(self):
        """
        Returns the exchange address
        """
        if self.contract_config:
            return self.contract_config.get_exchange()

    def get_executor_address(self):
        """
        Returns the executor address
        """
        if self.contract_config:
            return self.contract_config.get_executor()

    
    
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

    def create_api_key(self, nonce : int = None):
        """
        Creates a new CLOB API key for the given 
        """
        self.assert_level_1_auth()
        
        endpoint = "{}{}".format(self.host, CREATE_API_KEY)
        headers= create_level_1_headers(self.signer, nonce)
        
        creds = post(endpoint, headers=headers)
        self.logger.info(creds)
        return creds

    def derive_api_key(self, nonce : int = None):
        """
        Derives an already existing CLOB API key for the given address and nonce 
        """
        self.assert_level_1_auth()
        
        endpoint = "{}{}".format(self.host, DERIVE_API_KEY)
        headers= create_level_1_headers(self.signer, nonce)
        
        creds = get(endpoint, headers=headers)
        self.logger.info(creds)
        return creds

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

    def get_midpoint(self, tokenID):
        """
        Get the mid market price for the given market
        """
        return get("{}{}?market={}".format(self.host, MID_POINT, tokenID))

    def get_price(self, tokenID, side):
        """
        Get the market price for the given market
        """
        return get("{}{}?price={}&side={}".format(self.host, PRICE, tokenID, side))

    def create_limit_order(self, order_args: LimitOrderArgs):
        """
        Creates and signs a limit order
        Level 2 Auth required
        """
        self.assert_level_2_auth()

        return self.builder.create_limit_order(order_args)

    def create_market_order(self, order_args: MarketOrderArgs):
        """
        Creates and signs a market order
        Level 2 Auth required
        """
        self.assert_level_2_auth()
        return self.builder.create_market_order(order_args)

    def post_order(self, order):
        """
        Posts the order
        """
        self.assert_level_2_auth()
        body = order.dict()
        headers = create_level_2_headers(self.signer, self.creds, RequestArgs(method="POST", request_path=POST_ORDER, body=body))
        return post("{}{}".format(self.host, POST_ORDER), headers=headers, data=body)

    def create_and_post_limit_order(self, order_args: LimitOrderArgs):
        """
        Utility function to create and publish a limit order
        """
        lim = self.create_limit_order(order_args)
        return self.post_order(lim)

    def create_and_post_market_order(self, order_args: MarketOrderArgs):
        """
        Utility function to create and publish a market order
        """
        mkt = self.create_market_order(order_args)
        return self.post_order(mkt)

    def cancel(self, order_id):
        """
        Cancels an order
        Level 2 Auth required
        """
        self.assert_level_2_auth()
        body = {
            "orderID": order_id
        }

        request_args = RequestArgs(method="DELETE", request_path=CANCEL, body=body)
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        return delete("{}{}".format(self.host, CANCEL), headers=headers, data=body)

    def cancel_all(self):
        """
        Cancels all available orders for the user
        Level 2 Auth required
        """
        self.assert_level_2_auth()
        request_args = RequestArgs(method="DELETE", request_path=CANCEL_ALL)
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        return delete("{}{}".format(self.host, CANCEL_ALL), headers=headers)

    def get_open_orders(self, params: FilterParams = None):
        """
        Gets open orders for the API key
        Requires Level 2 authentication
        """
        self.assert_level_2_auth()
        request_args = RequestArgs(method="GET", request_path=OPEN_ORDERS)
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        url = add_query_params("{}{}".format(self.host, OPEN_ORDERS), params)
        return get(url, headers=headers)

    def get_order_book(self, token_id):
        """
        Fetches the orderbook for the token_id
        """
        return get("{}{}?market={}".format(self.host, GET_ORDER_BOOK, token_id))

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

    def get_trade_history(self, params: FilterParams=None):
        """
        Fetches the trade history for a user
        Requires Level 2 authentication
        """
        self.assert_level_2_auth()
        request_args = RequestArgs(method="GET", request_path=TRADE_HISTORY)
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        url = add_query_params("{}{}".format(self.host, TRADE_HISTORY), params)
        return get(url, headers=headers)
    
    def get_order_history(self, params: FilterParams = None):
        """
        Fetches order history for a user
        Requires Level 2 Authentication
        """
        self.assert_level_2_auth()
        request_args = RequestArgs(method="GET", request_path=ORDER_HISTORY)
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        url = add_query_params("{}{}".format(self.host, ORDER_HISTORY), params)
        return get(url, headers=headers)
    
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
            


