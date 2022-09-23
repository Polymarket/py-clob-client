from py_order_utils.builders import OrderBuilder as UtilsOrderBuild
from py_order_utils.model import EOA, OrderData, SignedOrder
from py_order_utils.config import get_contract_config

from .helpers import to_token_decimals
from .constants import BUY

from ..signer import Signer
from ..clob_types import OrderArgs


class OrderBuilder:
    def __init__(self, signer: Signer, sig_type=None, funder=None):
        self.signer = signer

        # Signature type used sign orders, defaults to EOA type
        self.sig_type = sig_type if sig_type is not None else EOA

        # Address which holds funds to be used.
        # Used for Polymarket proxy wallets and other smart contract wallets
        # Defaults to the address of the signer
        self.funder = funder if funder is not None else self.signer.address()
        self.contract_config = self._get_contract_config(self.signer.get_chain_id())
        self.order_builder = UtilsOrderBuild(
            self.contract_config.exchange, self.signer.get_chain_id(), self.signer
        )

    def _get_contract_config(self, chain_id: int):
        return get_contract_config(chain_id)

    def create_order(self, order_args: OrderArgs) -> SignedOrder:
        """
        Creates and signs an order
        """
        if order_args.side == BUY:
            side = 0
            maker_amount = to_token_decimals(order_args.price * order_args.size)
            taker_amount = to_token_decimals(order_args.size)
        else:
            side = 1
            maker_amount = to_token_decimals(order_args.size)
            taker_amount = to_token_decimals(order_args.price * order_args.size)

        data = OrderData(
            maker=self.funder,
            taker=order_args.taker,
            tokenId=order_args.token_id,
            makerAmount=maker_amount,
            takerAmount=taker_amount,
            side=side,
            feeRateBps=str(order_args.fee_rate_bps),
            nonce=str(order_args.nonce),
            signer=self.signer.address(),
            expiration=str(order_args.expiration),
            signatureType=self.sig_type,
        )

        return self.order_builder.build_signed_order(data)
