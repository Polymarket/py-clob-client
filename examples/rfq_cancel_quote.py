"""
Example: Cancel an RFQ quote (Maker side)

This script demonstrates how a maker can cancel their quote.
"""

import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.rfq import CancelRfqQuoteParams
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

    quote_id = os.getenv("RFQ_QUOTE_ID")

    if not quote_id:
        print("RFQ_QUOTE_ID not provided. Please set this environment variable.")
        return

    print(f"Cancelling RFQ quote: {quote_id}")

    cancel_params = CancelRfqQuoteParams(quote_id=quote_id)

    try:
        response = client.rfq.cancel_rfq_quote(cancel_params)
        print(f"Response: {response}")

        if response == "OK":
            print("\nRFQ quote cancelled successfully!")
        else:
            print(f"\nCancel returned: {response}")
    except Exception as e:
        print(f"\nError cancelling quote: {e}")

    print("\nDone!")


if __name__ == "__main__":
    main()
