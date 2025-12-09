"""
RFQ (Request for Quote) client for the Polymarket CLOB API.

This module provides the RfqClient class which handles all RFQ operations
including creating requests, quotes, and executing trades.
"""

import logging
from typing import Optional, Any, TYPE_CHECKING

from ..clob_types import RequestArgs, OrderArgs, PartialCreateOrderOptions
from ..headers.headers import create_level_2_headers
from ..http_helpers.helpers import get, post, delete
from ..order_builder.builder import ROUNDING_CONFIG
from ..order_builder.helpers import round_normal, round_down
from ..order_builder.constants import BUY, SELL
from ..endpoints import (
    CREATE_RFQ_REQUEST,
    CANCEL_RFQ_REQUEST,
    GET_RFQ_REQUESTS,
    CREATE_RFQ_QUOTE,
    CANCEL_RFQ_QUOTE,
    GET_RFQ_QUOTES,
    GET_RFQ_BEST_QUOTE,
    RFQ_REQUESTS_ACCEPT,
    RFQ_QUOTE_APPROVE,
    RFQ_CONFIG,
)

from .rfq_types import (
    RfqUserOrder,
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
)
from .rfq_helpers import (
    parse_units,
    parse_rfq_requests_params,
    parse_rfq_quotes_params,
    COLLATERAL_TOKEN_DECIMALS,
)

if TYPE_CHECKING:
    from ..client import ClobClient


class RfqClient:
    """
    RFQ client for creating and managing RFQ requests and quotes.

    This client is typically accessed via the parent ClobClient's `rfq` attribute:

        client = ClobClient(host, chain_id, key, creds)
        request_params = client.rfq.create_rfq_request(user_order)
        response = client.rfq.post_rfq_request(request_params)
    """

    def __init__(self, parent: "ClobClient"):
        """
        Initialize the RFQ client.

        Args:
            parent: The parent ClobClient instance providing auth and config.
        """
        self._parent = parent
        self.logger = logging.getLogger(self.__class__.__name__)

    def _ensure_l2_auth(self) -> None:
        """
        Verify that L2 authentication is available.

        Raises:
            PolyException: If signer or creds are not configured.
        """
        self._parent.assert_level_2_auth()

    def _get_l2_headers(self, method: str, endpoint: str, body: Any = None) -> dict:
        """
        Create L2 authentication headers for a request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            body: Optional request body

        Returns:
            Dictionary of authentication headers.
        """
        request_args = RequestArgs(method=method, request_path=endpoint, body=body)
        return create_level_2_headers(
            self._parent.signer,
            self._parent.creds,
            request_args,
        )

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        return f"{self._parent.host}{endpoint}"

    # =========================================================================
    # Request-side methods
    # =========================================================================

    def create_rfq_request(
        self,
        user_order: RfqUserOrder,
        options: Optional[PartialCreateOrderOptions] = None,
    ) -> dict:
        """
        Create and post an RFQ request from a user order.

        This method:
        1. Resolves the tick size for the token
        2. Rounds price and size according to tick size rules
        3. Calculates amount_in and amount_out based on side
        4. Posts the request to the server

        Args:
            user_order: Simplified order with token_id, price, side, size
            options: Optional tick size override

        Returns:
            Response dict with request_id on success.

        Example:
            >>> response = client.rfq.create_rfq_request(
            ...     RfqUserOrder(
            ...         token_id="123...",
            ...         price=0.5,
            ...         side="BUY",
            ...         size=40,
            ...     )
            ... )
        """
        token_id = user_order.token_id
        price = user_order.price
        side = user_order.side
        size = user_order.size

        # Resolve tick size (from options or fetch from server)
        tick_size = self._parent._ClobClient__resolve_tick_size(
            token_id,
            options.tick_size if options else None,
        )

        # Get rounding configuration
        round_config = ROUNDING_CONFIG[tick_size]

        # Round price and size
        rounded_price = round_normal(price, round_config.price)
        rounded_size = round_down(size, round_config.size)

        # Format with correct decimal places
        price_decimals = int(round_config.price)
        size_decimals = int(round_config.size)
        amount_decimals = int(round_config.amount)

        rounded_price_str = f"{rounded_price:.{price_decimals}f}"
        rounded_size_str = f"{rounded_size:.{size_decimals}f}"

        # Parse back to numbers for calculation
        size_num = float(rounded_size_str)
        price_num = float(rounded_price_str)

        # Get signature type from parent's order builder
        user_type = self._parent.builder.sig_type

        # Calculate amounts based on side
        if side == BUY:
            # Buying tokens: pay USDC, receive tokens
            # asset_in = tokens (what taker receives)
            # asset_out = USDC (what taker pays)
            amount_in = parse_units(rounded_size_str, COLLATERAL_TOKEN_DECIMALS)

            usdc_amount = size_num * price_num
            usdc_amount_str = f"{usdc_amount:.{amount_decimals}f}"
            amount_out = parse_units(usdc_amount_str, COLLATERAL_TOKEN_DECIMALS)

            asset_in = token_id
            asset_out = "0"  # USDC
        else:
            # Selling tokens: pay tokens, receive USDC
            # asset_in = USDC (what taker receives)
            # asset_out = tokens (what taker pays)
            usdc_amount = size_num * price_num
            usdc_amount_str = f"{usdc_amount:.{amount_decimals}f}"
            amount_in = parse_units(usdc_amount_str, COLLATERAL_TOKEN_DECIMALS)

            amount_out = parse_units(rounded_size_str, COLLATERAL_TOKEN_DECIMALS)

            asset_in = "0"  # USDC
            asset_out = token_id

        params = CreateRfqRequestParams(
            asset_in=asset_in,
            asset_out=asset_out,
            amount_in=str(amount_in),
            amount_out=str(amount_out),
            user_type=user_type,
        )

        return self.post_rfq_request(params)

    def post_rfq_request(self, payload: CreateRfqRequestParams) -> dict:
        """
        Post an RFQ request to the server.

        Args:
            payload: Request parameters from create_rfq_request()

        Returns:
            Response dict with request_id on success.
        """
        self._ensure_l2_auth()

        body = {
            "assetIn": payload.asset_in,
            "assetOut": payload.asset_out,
            "amountIn": payload.amount_in,
            "amountOut": payload.amount_out,
            "userType": payload.user_type,
        }

        headers = self._get_l2_headers("POST", CREATE_RFQ_REQUEST, body)
        return post(self._build_url(CREATE_RFQ_REQUEST), headers=headers, data=body)

    def cancel_rfq_request(self, params: CancelRfqRequestParams) -> str:
        """
        Cancel an RFQ request.

        Args:
            params: Contains request_id to cancel.

        Returns:
            "OK" on success.
        """
        self._ensure_l2_auth()

        body = {"requestId": params.request_id}

        headers = self._get_l2_headers("DELETE", CANCEL_RFQ_REQUEST, body)
        return delete(self._build_url(CANCEL_RFQ_REQUEST), headers=headers, data=body)

    def get_rfq_requests(
        self, params: Optional[GetRfqRequestsParams] = None
    ) -> dict:
        """
        Get RFQ requests with optional filtering.

        Args:
            params: Optional filter parameters.

        Returns:
            Paginated response with RFQ requests.
        """
        self._ensure_l2_auth()

        headers = self._get_l2_headers("GET", GET_RFQ_REQUESTS)
        query_params = parse_rfq_requests_params(params)

        # Build URL with query params
        url = self._build_url(GET_RFQ_REQUESTS)
        if query_params:
            query_string = "&".join(f"{k}={v}" for k, v in query_params.items())
            url = f"{url}?{query_string}"

        return get(url, headers=headers)

    # =========================================================================
    # Quote-side methods
    # =========================================================================

    def create_rfq_quote(
        self,
        user_quote: RfqUserQuote,
        options: Optional[PartialCreateOrderOptions] = None,
    ) -> dict:
        """
        Create and post an RFQ quote from a user quote.

        This method:
        1. Fetches the RFQ request to get token, side, and size
        2. Resolves the tick size for the token
        3. Rounds price according to tick size rules
        4. Calculates amount_in and amount_out based on the quoted price
        5. Posts the quote to the server

        Args:
            user_quote: Simplified quote with request_id and price
            options: Optional tick size override

        Returns:
            Response dict with quote_id on success.

        Example:
            >>> response = client.rfq.create_rfq_quote(
            ...     RfqUserQuote(
            ...         request_id="abc123",
            ...         price=0.52,
            ...     )
            ... )
        """
        # Step 1: Fetch the RFQ request to get details
        rfq_requests = self.get_rfq_requests(
            GetRfqRequestsParams(request_ids=[user_quote.request_id])
        )

        if not rfq_requests.get("data") or len(rfq_requests["data"]) == 0:
            raise Exception("RFQ request not found")

        rfq_request = rfq_requests["data"][0]

        token_id = rfq_request.get("token")
        side = rfq_request.get("side", BUY)
        price = user_quote.price

        # Get size from request (sizeIn for BUY, sizeOut for SELL from requester's perspective)
        # Quoter takes the opposite side
        if side == BUY:
            size = rfq_request.get("sizeIn") or rfq_request.get("size_in")
        else:
            size = rfq_request.get("sizeOut") or rfq_request.get("size_out")

        # Step 2: Resolve tick size
        tick_size = self._parent._ClobClient__resolve_tick_size(
            token_id,
            options.tick_size if options else None,
        )

        # Get rounding configuration
        round_config = ROUNDING_CONFIG[tick_size]

        # Round price
        rounded_price = round_normal(price, round_config.price)

        # Format with correct decimal places
        price_decimals = int(round_config.price)
        size_decimals = int(round_config.size)
        amount_decimals = int(round_config.amount)

        rounded_price_str = f"{rounded_price:.{price_decimals}f}"
        size_str = f"{float(size):.{size_decimals}f}"

        # Parse back to numbers for calculation
        size_num = float(size_str)
        price_num = float(rounded_price_str)

        # Get signature type from parent's order builder
        user_type = self._parent.builder.sig_type

        # Step 3: Calculate amounts based on side
        # Quoter takes the opposite side of the requester
        if side == BUY:
            # Requester wants to BUY tokens, so quoter SELLs tokens
            # Quoter pays tokens (asset_out), receives USDC (asset_in)
            amount_out = parse_units(size_str, COLLATERAL_TOKEN_DECIMALS)

            usdc_amount = size_num * price_num
            usdc_amount_str = f"{usdc_amount:.{amount_decimals}f}"
            amount_in = parse_units(usdc_amount_str, COLLATERAL_TOKEN_DECIMALS)

            asset_in = "0"  # USDC
            asset_out = token_id
        else:
            # Requester wants to SELL tokens, so quoter BUYs tokens
            # Quoter pays USDC (asset_out), receives tokens (asset_in)
            amount_in = parse_units(size_str, COLLATERAL_TOKEN_DECIMALS)

            usdc_amount = size_num * price_num
            usdc_amount_str = f"{usdc_amount:.{amount_decimals}f}"
            amount_out = parse_units(usdc_amount_str, COLLATERAL_TOKEN_DECIMALS)

            asset_in = token_id
            asset_out = "0"  # USDC

        params = CreateRfqQuoteParams(
            request_id=user_quote.request_id,
            asset_in=asset_in,
            asset_out=asset_out,
            amount_in=str(amount_in),
            amount_out=str(amount_out),
        )

        return self.post_rfq_quote(params)

    def post_rfq_quote(self, payload: CreateRfqQuoteParams) -> dict:
        """
        Post an RFQ quote to the server.

        Args:
            payload: Quote parameters from create_rfq_quote()

        Returns:
            Response dict with quote_id on success.
        """
        self._ensure_l2_auth()

        # Get signature type from parent's order builder
        user_type = self._parent.builder.sig_type

        body = {
            "requestId": payload.request_id,
            "assetIn": payload.asset_in,
            "assetOut": payload.asset_out,
            "amountIn": payload.amount_in,
            "amountOut": payload.amount_out,
            "userType": user_type,
        }

        headers = self._get_l2_headers("POST", CREATE_RFQ_QUOTE, body)
        return post(self._build_url(CREATE_RFQ_QUOTE), headers=headers, data=body)

    def get_rfq_quotes(self, params: Optional[GetRfqQuotesParams] = None) -> dict:
        """
        Get RFQ quotes with optional filtering.

        Args:
            params: Optional filter parameters.

        Returns:
            Paginated response with RFQ quotes.
        """
        self._ensure_l2_auth()

        headers = self._get_l2_headers("GET", GET_RFQ_QUOTES)
        query_params = parse_rfq_quotes_params(params)

        # Build URL with query params
        url = self._build_url(GET_RFQ_QUOTES)
        if query_params:
            query_string = "&".join(f"{k}={v}" for k, v in query_params.items())
            url = f"{url}?{query_string}"

        return get(url, headers=headers)

    def get_rfq_best_quote(
        self, params: Optional[GetRfqBestQuoteParams] = None
    ) -> dict:
        """
        Get the best quote for an RFQ request.

        Args:
            params: Contains request_id.

        Returns:
            Single quote object representing the best quote.
        """
        self._ensure_l2_auth()

        headers = self._get_l2_headers("GET", GET_RFQ_BEST_QUOTE)

        url = self._build_url(GET_RFQ_BEST_QUOTE)
        if params and params.request_id:
            url = f"{url}?requestId={params.request_id}"

        return get(url, headers=headers)

    def cancel_rfq_quote(self, params: CancelRfqQuoteParams) -> str:
        """
        Cancel an RFQ quote.

        Args:
            params: Contains quote_id to cancel.

        Returns:
            "OK" on success.
        """
        self._ensure_l2_auth()

        body = {"quoteId": params.quote_id}

        headers = self._get_l2_headers("DELETE", CANCEL_RFQ_QUOTE, body)
        return delete(self._build_url(CANCEL_RFQ_QUOTE), headers=headers, data=body)

    # =========================================================================
    # Trade execution methods
    # =========================================================================

    def accept_rfq_quote(self, params: AcceptQuoteParams) -> str:
        """
        Accept an RFQ quote (requester side).

        This method:
        1. Fetches the RFQ quote details
        2. Creates a signed order matching the quote
        3. Submits the acceptance with the order

        Args:
            params: Contains request_id, quote_id, and expiration.

        Returns:
            "OK" on success.
        """
        self._ensure_l2_auth()

        # Step 1: Fetch the RFQ request
        rfq_requests = self.get_rfq_requests(
            GetRfqRequestsParams(request_ids=[params.request_id])
        )

        if not rfq_requests.get("data") or len(rfq_requests["data"]) == 0:
            raise Exception("RFQ request not found")

        rfq_request = rfq_requests["data"][0]

        # Step 2: Create an order based on request details
        # Requester keeps their original side
        side = rfq_request.get("side", BUY)

        # Determine size based on request side
        if side == BUY:
            size = rfq_request.get("sizeIn")
        else:
            size = rfq_request.get("sizeOut")

        token_id = rfq_request.get("token")
        price = rfq_request.get("price")

        order_args = OrderArgs(
            token_id=token_id,
            price=float(price),
            size=float(size),
            side=side,
            expiration=params.expiration,
        )

        order = self._parent.create_order(order_args)

        if not order:
            raise Exception("Error creating order")

        # Step 3: Build accept payload
        order_dict = order.dict()

        accept_payload = {
            "requestId": params.request_id,
            "quoteId": params.quote_id,
            "owner": self._parent.creds.api_key,
            # Order fields from dict
            "salt": int(order_dict["salt"]),
            "maker": order_dict["maker"],
            "signer": order_dict["signer"],
            "taker": order_dict["taker"],
            "tokenId": order_dict["tokenId"],
            "makerAmount": order_dict["makerAmount"],
            "takerAmount": order_dict["takerAmount"],
            "expiration": int(order_dict["expiration"]),
            "nonce": order_dict["nonce"],
            "feeRateBps": order_dict["feeRateBps"],
            "side": side,
            "signatureType": int(order_dict["signatureType"]),
            "signature": order_dict["signature"],
        }

        self.logger.debug(
            "Accept payload: requestId=%s, quoteId=%s, tokenId=%s, side=%s",
            accept_payload.get("requestId"),
            accept_payload.get("quoteId"),
            accept_payload.get("tokenId"),
            accept_payload.get("side"),
        )

        headers = self._get_l2_headers("POST", RFQ_REQUESTS_ACCEPT, accept_payload)
        return post(
            self._build_url(RFQ_REQUESTS_ACCEPT),
            headers=headers,
            data=accept_payload,
        )

    def approve_rfq_order(self, params: ApproveOrderParams) -> str:
        """
        Approve an RFQ order (quoter side).

        This method:
        1. Fetches the RFQ quote details
        2. Creates a signed order based on quote parameters
        3. Submits the approval with the order

        Args:
            params: Contains request_id, quote_id, and expiration.

        Returns:
            "OK" on success.
        """
        self._ensure_l2_auth()

        # Step 1: Fetch the RFQ quote
        rfq_quotes = self.get_rfq_quotes(
            GetRfqQuotesParams(quote_ids=[params.quote_id])
        )

        if not rfq_quotes.get("data") or len(rfq_quotes["data"]) == 0:
            raise Exception("RFQ quote not found")

        rfq_quote = rfq_quotes["data"][0]

        # Step 2: Create an order based on quote details
        # Quoter uses their own quote's side
        side = rfq_quote.get("side", BUY)

        # Determine size based on quote side
        if side == BUY:
            size = rfq_quote.get("sizeIn")
        else:
            size = rfq_quote.get("sizeOut")

        token_id = rfq_quote.get("token")
        price = rfq_quote.get("price")

        order_args = OrderArgs(
            token_id=token_id,
            price=float(price),
            size=float(size),
            side=side,
            expiration=params.expiration,
        )

        order = self._parent.create_order(order_args)

        if not order:
            raise Exception("Error creating order")

        # Step 3: Build approve payload
        order_dict = order.dict()

        approve_payload = {
            "requestId": params.request_id,
            "quoteId": params.quote_id,
            "owner": self._parent.creds.api_key,
            # Order fields from dict
            "salt": int(order_dict["salt"]),
            "maker": order_dict["maker"],
            "signer": order_dict["signer"],
            "taker": order_dict["taker"],
            "tokenId": order_dict["tokenId"],
            "makerAmount": order_dict["makerAmount"],
            "takerAmount": order_dict["takerAmount"],
            "expiration": int(order_dict["expiration"]),
            "nonce": order_dict["nonce"],
            "feeRateBps": order_dict["feeRateBps"],
            "side": side,
            "signatureType": int(order_dict["signatureType"]),
            "signature": order_dict["signature"],
        }

        headers = self._get_l2_headers("POST", RFQ_QUOTE_APPROVE, approve_payload)
        return post(
            self._build_url(RFQ_QUOTE_APPROVE),
            headers=headers,
            data=approve_payload,
        )

    # =========================================================================
    # Configuration
    # =========================================================================

    def rfq_config(self) -> dict:
        """
        Get RFQ configuration from the server.

        Returns:
            Configuration object with RFQ system parameters.
        """
        self._ensure_l2_auth()

        headers = self._get_l2_headers("GET", RFQ_CONFIG)
        return get(self._build_url(RFQ_CONFIG), headers=headers)
