"""
Example: Cancel an RFQ request (Taker side)

This script demonstrates how a taker can cancel their RFQ request.
"""

import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.rfq import CancelRfqRequestParams
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

    if not request_id:
        print("RFQ_REQUEST_ID not provided. Please set this environment variable.")
        return

    print(f"Cancelling RFQ request: {request_id}")

    cancel_params = CancelRfqRequestParams(request_id=request_id)

    try:
        response = client.rfq.cancel_rfq_request(cancel_params)
        print(f"Response: {response}")

        if response == "OK":
            print("\nRFQ request cancelled successfully!")
        else:
            print(f"\nCancel returned: {response}")
    except Exception as e:
        print(f"\nError cancelling request: {e}")

    print("\nDone!")


if __name__ == "__main__":
    main()
