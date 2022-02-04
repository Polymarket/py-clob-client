from py_order_utils.builders import LimitOrderBuilder
from py_order_utils.model import EOA, LimitOrderData
from py_order_utils.config import get_contract_config

from .helpers import round_down, to_collateral_token_decimals, to_conditional_token_decimals
from .constants import BUY

from ..signer import Signer
from ..clob_types import LimitOrderArgs


class OrderBuilder:
    
    def __init__(self, signer: Signer, sig_type=EOA, funder=None):
        """
        """
        self.signer = signer
        
        # Signature type used sign Limit and Market orders, defaults to EOA type
        self.sig_type = sig_type

        # Address which holds funds to be used.
        # Used for Polymarket proxy wallets and other smart contract wallets
        # If not provided, funderAddress is the signer address
        self.funder = funder if funder is not None else self.signer.address
        self.contract_config = self._get_contract_config(self.signer.get_chain_id())
        self.limit_order_builder = self._create_limit_order_builder()

    def _get_contract_config(self, chain_id: int):
        return get_contract_config(chain_id)

    def _create_limit_order_builder(self):
        return LimitOrderBuilder(self.contract_config.exchange, self.signer.chain_id, self.signer)


    def create_limit_order(self, order_args: LimitOrderArgs):
        """
        Creates and signs a limit order
        """
        if order_args.side == BUY:
            maker_asset = self.contract_config.get_collateral()
            # taker_asset = conditional_token TODO: update when py_order_utils has the conditional token
            taker_asset = "0x0000000000000000000000000000000000000000"
            maker_asset_id = None
            taker_asset_id = int(order_args.token_id)

            size_2_digits = round_down(order_args.size, 2)
            maker_amount = to_collateral_token_decimals(round_down(order_args.price * size_2_digits, 2))
            taker_amount = to_conditional_token_decimals(size_2_digits)
        else:
            maker_asset = "0x0000000000000000000000000000000000000000" #same TODO as above
            taker_asset = self.contract_config.get_collateral()
            maker_asset_id = int(order_args.token_id)
            taker_asset_id = None

            size_2_digits = round_down(order_args.size, 2)
            maker_amount = to_conditional_token_decimals(size_2_digits)
            taker_amount = to_collateral_token_decimals(round_down(order_args.price * size_2_digits, 2))
        
        #TODO: move some functions to helpers
        limit_order = self.limit_order_builder.build_limit_order(LimitOrderData(
                exchange_address=self.contract_config.exchange,
                maker_asset_address=maker_asset,
                maker_asset_id=maker_asset_id,
                taker_asset_address=taker_asset,
                taker_asset_id=taker_asset_id,
                maker_address=self.funder,
                maker_amount=maker_amount,
                taker_amount=taker_amount,
                signer=self.signer.address,
                sig_type=self.sig_type
            )
        )
        signature = self.limit_order_builder.build_limit_order_signature(limit_order)
        return self.limit_order_builder.build_limit_order_and_signature(limit_order, signature)


    

    

