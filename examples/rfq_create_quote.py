"""
Example: Create an RFQ quote (Maker side)

This script demonstrates how a maker can provide a quote
in response to an RFQ request.
"""

import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.rfq import (
    CreateRfqQuoteParams,
    GetRfqRequestsParams,
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


    # Fetch the specific request
    request_id = "019aed55-087a-7b19-9b72-89416c0604a1"
    params = GetRfqRequestsParams(request_ids=[request_id])
    print(f"Fetching request: {request_id}")
    response = client.rfq.get_rfq_requests(params)

    if not response.get("data") or len(response["data"]) == 0:
        print(f"Request {request_id} not found. Exiting.")
        return


    quote_params = CreateRfqQuoteParams(
        request_id=request_id,
        asset_in="0",  # Maker recieves USDC
        asset_out="34097058504275310827233323421517291090691602969494795225921954353603704046623",  # Maker pays tokens
        amount_in="50000000",
        amount_out="100000000",
    )

    print(f"\nCreating quote for request {request_id}...")
    print(f"  Asset In: {quote_params.asset_in}")
    print(f"  Asset Out: {quote_params.asset_out}")
    print(f"  Amount In: {quote_params.amount_in}")
    print(f"  Amount Out: {quote_params.amount_out}")

    response = client.rfq.create_rfq_quote(quote_params)

    print(f"\nResponse: {response}")
    if "quoteId" in response:
        print(f"\nQuote created successfully!")
        print(f"Quote ID: {response['quoteId']}")
    else:
        print(f"\nFailed to create quote")

    print("\nDone!")


if __name__ == "__main__":
    main()
