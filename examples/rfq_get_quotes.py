"""
Example: Get RFQ quotes

This script demonstrates how to fetch RFQ quotes with various filters.
"""

import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.rfq import GetRfqQuotesParams, GetRfqBestQuoteParams
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

    # Get quotes for a specific request
    request_id = os.getenv("RFQ_REQUEST_ID")

    if request_id:
        print(f"Fetching quotes for request: {request_id}")
        params = GetRfqQuotesParams(request_ids=[request_id])
        response = client.rfq.get_rfq_quotes(params)

        if "data" in response:
            quotes = response["data"]
            print(f"Found {len(quotes)} quotes\n")

            for quote in quotes:
                print(f"Quote ID: {quote.get('quoteId', quote.get('quote_id'))}")
                print(f"  Request ID: {quote.get('requestId', quote.get('request_id'))}")
                print(f"  Token: {quote.get('token')}")
                print(f"  Side: {quote.get('side')}")
                print(f"  Price: {quote.get('price')}")
                print(f"  Size In: {quote.get('sizeIn', quote.get('size_in'))}")
                print(f"  Size Out: {quote.get('sizeOut', quote.get('size_out'))}")
                print(f"  State: {quote.get('state')}")
                print()
        else:
            print(f"Response: {response}")

        # Get best quote for the request
        print(f"\nFetching best quote for request: {request_id}")
        best_quote_params = GetRfqBestQuoteParams(request_id=request_id)
        best_quote = client.rfq.get_rfq_best_quote(best_quote_params)
        print(f"Best quote: {best_quote}")

    else:
        # Get all quotes
        print("Fetching all quotes (no RFQ_REQUEST_ID provided)...")
        params = GetRfqQuotesParams(limit=10)
        response = client.rfq.get_rfq_quotes(params)

        if "data" in response:
            quotes = response["data"]
            print(f"Found {len(quotes)} quotes\n")

            for quote in quotes:
                print(f"Quote ID: {quote.get('quoteId', quote.get('quote_id'))}")
                print(f"  Request ID: {quote.get('requestId', quote.get('request_id'))}")
                print(f"  Price: {quote.get('price')}")
                print(f"  State: {quote.get('state')}")
                print()
        else:
            print(f"Response: {response}")

    print("\nDone!")


if __name__ == "__main__":
    main()
