"""
Example: Cancel an RFQ request (Taker side)

This script demonstrates how a taker can cancel their RFQ request.
"""

import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.rfq import CancelRfqRequestParams
from dotenv import load_dotenv
from py_clob_client.constants import AMOY


load_dotenv()


def main():
    host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    chain_id = int(os.getenv("CHAIN_ID", AMOY))
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    cancel_params = CancelRfqRequestParams(request_id="019aed34-9c9f-71e8-976f-0ed0f783d0a0")

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
