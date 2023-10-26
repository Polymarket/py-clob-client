from ..clob_types import ApiCreds, RequestArgs
from ..signing.hmac import build_hmac_signature
from ..signer import Signer
from ..signing.eip712 import sign_clob_auth_message
from datetime import datetime

POLY_ADDRESS = "POLY_ADDRESS"
POLY_SIGNATURE = "POLY_SIGNATURE"
POLY_TIMESTAMP = "POLY_TIMESTAMP"
POLY_NONCE = "POLY_NONCE"
POLY_API_KEY = "POLY_API_KEY"
POLY_PASSPHRASE = "POLY_PASSPHRASE"


def create_level_1_headers(signer: Signer, nonce: int = None):
    """
    Creates Level 1 Poly headers for a request
    """
    timestamp = int(datetime.now().timestamp())

    n = 0
    if nonce is not None:
        n = nonce

    signature = sign_clob_auth_message(signer, timestamp, n)
    headers = {
        POLY_ADDRESS: signer.address(),
        POLY_SIGNATURE: signature,
        POLY_TIMESTAMP: str(timestamp),
        POLY_NONCE: str(n),
    }

    return headers


def create_level_2_headers(signer: Signer, creds: ApiCreds, request_args: RequestArgs):
    """
    Creates Level 2 Poly headers for a request
    """
    timestamp = int(datetime.now().timestamp())

    hmac_sig = build_hmac_signature(
        creds.api_secret,
        timestamp,
        request_args.method,
        request_args.request_path,
        request_args.body,
    )

    return {
        POLY_ADDRESS: signer.address(),
        POLY_SIGNATURE: hmac_sig,
        POLY_TIMESTAMP: str(timestamp),
        POLY_API_KEY: creds.api_key,
        POLY_PASSPHRASE: creds.api_passphrase,
    }
