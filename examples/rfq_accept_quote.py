import os
import time

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.rfq import AcceptQuoteParams
from py_clob_client.constants import AMOY
from dotenv import load_dotenv

load_dotenv()


def main():
    host = os.getenv("CLOB_API_URL", "https://clob-staging.polymarket.com/")
    chain_id = int(os.getenv("CHAIN_ID", AMOY))
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    # Accept a quote (requester side)
    # Refers to the order expiry, not request expiry. For request expiry, check the server RFQ config.
    expiration = int(time.time()) + 3600

    accept_params = AcceptQuoteParams(
        request_id="019b04a4-2f4b-73b3-8fa2-2760b2754601",
        quote_id="019b04a7-5205-7eeb-9a48-227e8d53bd17",
        expiration=expiration,
    )

    resp = client.rfq.accept_rfq_quote(accept_params)
    print(resp)
    print("Done!")


main()
