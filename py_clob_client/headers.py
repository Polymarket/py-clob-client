from .signer import Signer
from .signing.eip712 import sign_clob_auth_message
from datetime import datetime


POLY_ADDRESS = "POLY_ADDRESS"
POLY_SIGNATURE = "POLY_SIGNATURE"
POLY_TIMESTAMP = "POLY_TIMESTAMP"


def create_level_1_headers(signer: Signer):
    """
    Creates Level 1 Poly headers for a request
    """
    timestamp = int(datetime.now().timestamp())
    signature = sign_clob_auth_message(signer, timestamp)
    headers = {
        POLY_ADDRESS: signer.address,
        POLY_SIGNATURE: signature,
        POLY_TIMESTAMP: str(timestamp),
    }
    return headers
