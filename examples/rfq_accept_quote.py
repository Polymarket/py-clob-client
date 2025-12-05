"""
Example: Accept an RFQ quote (Taker side)

This script demonstrates how a taker can accept a quote
and execute the trade.
"""

import os
import time

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.rfq import (
    AcceptQuoteParams,
)
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

    request_id = "019aed55-087a-7b19-9b72-89416c0604a1"
    quote_id = "019aed6a-4c0a-78aa-8d0a-cb99feb6029b"

    if not request_id:
        print("RFQ_REQUEST_ID not provided.")
        return

    if not quote_id:
        print("RFQ_QUOTE_ID not provided.")
        return

    # Set expiration to 1 hour from now
    expiration = int(time.time()) + 3600

    print(f"\nAccepting quote...")
    print(f"  Request ID: {request_id}")
    print(f"  Quote ID: {quote_id}")
    print(f"  Expiration: {expiration}")

    accept_params = AcceptQuoteParams(
        request_id=request_id,
        quote_id=quote_id,
        expiration=expiration,
    )

    try:
        response = client.rfq.accept_rfq_quote(accept_params)
        print(f"\nResponse: {response}")

        if response == "OK":
            print("\nQuote accepted successfully!")
            print("The maker now needs to approve the order to complete the trade.")
        else:
            print(f"\nQuote acceptance returned: {response}")
    except Exception as e:
        print(f"\nError accepting quote: {e}")

    print("\nDone!")


if __name__ == "__main__":
    main()
