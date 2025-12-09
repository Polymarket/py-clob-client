import os
import time

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.rfq import ApproveOrderParams
from py_clob_client.constants import AMOY
from dotenv import load_dotenv

load_dotenv()


def main():
    host = os.getenv("CLOB_API_URL", "https://clob-staging.polymarket.com/")
    chain_id = os.getenv("CHAIN_ID", AMOY)
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    # Approve an order (maker side)
    # Set expiration to 1 hour from now
    expiration = int(time.time()) + 3600

    approve_params = ApproveOrderParams(
        request_id="0xaaaa",
        quote_id="0xbbbb",
        expiration=expiration,
    )

    resp = client.rfq.approve_rfq_order(approve_params)
    print(resp)
    print("Done!")


main()
