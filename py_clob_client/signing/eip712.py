from eip712_structs import make_domain
from .model import ClobAuth
from ..signer import Signer
from web3 import Web3

CLOB_DOMAIN_NAME = "ClobAuthDomain"
CLOB_VERSION = "1"
MSG_TO_SIGN = "This message attests that I control the given wallet"

def get_clob_auth_domain():
    return make_domain(name=CLOB_DOMAIN_NAME, version=CLOB_VERSION, chainId=1)

def sign_clob_auth_message(signer: Signer, timestamp: int)-> str:
    clob_auth_msg = ClobAuth(address=signer.address, timestamp=str(timestamp), message=MSG_TO_SIGN)
    auth_struct_hash = Web3.keccak(clob_auth_msg.signable_bytes(get_clob_auth_domain()))
    return signer.sign(auth_struct_hash)


