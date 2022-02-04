from py_order_utils.builders import LimitOrderBuilder
from py_order_utils.model import EOA

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

    def create_limit_order(self, order_args: LimitOrderArgs):
        """
        """

        pass

    
    

