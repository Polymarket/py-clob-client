"""
Example: Approve an RFQ order (Maker side)

This script demonstrates how a maker can approve an order
after their quote has been accepted by the taker.
"""

import os
import time

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.rfq import ApproveOrderParams
from dotenv import load_dotenv


load_dotenv()


def main():
    host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    chain_id = int(os.getenv("CHAIN_ID", "137"))
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    request_id = os.getenv("RFQ_REQUEST_ID")
    quote_id = os.getenv("RFQ_QUOTE_ID")

    if not request_id:
        print("RFQ_REQUEST_ID not provided. Please set this environment variable.")
        return

    if not quote_id:
        print("RFQ_QUOTE_ID not provided. Please set this environment variable.")
        return

    # Set expiration to 1 hour from now
    expiration = int(time.time()) + 3600

    print(f"Approving order...")
    print(f"  Request ID: {request_id}")
    print(f"  Quote ID: {quote_id}")
    print(f"  Expiration: {expiration}")

    approve_params = ApproveOrderParams(
        request_id=request_id,
        quote_id=quote_id,
        expiration=expiration,
    )

    try:
        response = client.rfq.approve_rfq_order(approve_params)
        print(f"\nResponse: {response}")

        if response == "OK":
            print("\nOrder approved successfully!")
            print("The trade should now be executed.")
        else:
            print(f"\nOrder approval returned: {response}")
    except Exception as e:
        print(f"\nError approving order: {e}")

    print("\nDone!")


if __name__ == "__main__":
    main()
