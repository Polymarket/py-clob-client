from py_order_utils.builders import LimitOrderBuilder, MarketOrderBuilder
from py_order_utils.model import EOA, LimitOrderData, MarketOrderData
from py_order_utils.config import get_contract_config

from .helpers import round_down, to_token_decimals
from .constants import BUY

from ..signer import Signer
from ..clob_types import LimitOrderArgs, MarketOrderArgs


class OrderBuilder:
    
    def __init__(self, signer: Signer, sig_type=None, funder=None):
        self.signer = signer
        
        # Signature type used sign Limit and Market orders, defaults to EOA type
        self.sig_type = sig_type if sig_type is not None else EOA

        # Address which holds funds to be used.
        # Used for Polymarket proxy wallets and other smart contract wallets
        # Defaults to the address of the signer
        self.funder = funder if funder is not None else self.signer.address
        self.contract_config = self._get_contract_config(self.signer.get_chain_id())
        self.limit_order_builder = LimitOrderBuilder(self.contract_config.exchange, self.signer.chain_id, self.signer)
        self.market_order_builder = MarketOrderBuilder(self.contract_config.exchange, self.signer.chain_id, self.signer)

    def _get_contract_config(self, chain_id: int):
        return get_contract_config(chain_id)

    def create_limit_order(self, order_args: LimitOrderArgs):
        """
        Creates and signs a limit order
        """
        if order_args.side == BUY:
            maker_asset = self.contract_config.get_collateral()
            taker_asset = self.contract_config.get_conditional()
            maker_asset_id = None
            taker_asset_id = int(order_args.token_id)

            size_normalized = round_down(order_args.size, 2)
            maker_amount = to_token_decimals(round_down(order_args.price * size_normalized, 2))
            taker_amount = to_token_decimals(size_normalized)
        else:
            maker_asset = self.contract_config.get_conditional()
            taker_asset = self.contract_config.get_collateral()
            maker_asset_id = int(order_args.token_id)
            taker_asset_id = None

            size_normalized = round_down(order_args.size, 2)
            maker_amount = to_token_decimals(size_normalized)
            taker_amount = to_token_decimals(round_down(order_args.price * size_normalized, 2))

        data = LimitOrderData(
                exchange_address=self.contract_config.get_exchange(),
                maker_asset_address=maker_asset,
                maker_asset_id=maker_asset_id,
                taker_asset_address=taker_asset,
                taker_asset_id=taker_asset_id,
                maker_address=self.funder,
                taker_address=self.contract_config.get_executor(),
                maker_amount=maker_amount,
                taker_amount=taker_amount,
                signer=self.signer.address,
                sig_type=self.sig_type
        )
        
        return self.limit_order_builder.create_limit_order(data)

    def create_market_order(self, order_args: MarketOrderArgs):
        """
        """
        if order_args.side == BUY:
            maker_asset = self.contract_config.get_collateral()
            taker_asset = self.contract_config.get_conditional()
            maker_asset_id = None
            taker_asset_id = int(order_args.token_id)

            maker_amount = to_token_decimals(round_down(order_args.size, 2))
        else:
            maker_asset = self.contract_config.get_conditional()
            taker_asset = self.contract_config.get_collateral()
            maker_asset_id = int(order_args.token_id)
            taker_asset_id = None

            maker_amount = to_token_decimals(round_down(order_args.size, 2))

        data = MarketOrderData(
                exchange_address=self.contract_config.get_exchange(),
                maker_asset_address=maker_asset,
                maker_asset_id=maker_asset_id,
                taker_asset_address=taker_asset,
                taker_asset_id=taker_asset_id,
                maker_address=self.funder,
                maker_amount=maker_amount,
                signer=self.signer.address,
                sig_type=self.sig_type
        )        
        return self.market_order_builder.create_market_order(data)
