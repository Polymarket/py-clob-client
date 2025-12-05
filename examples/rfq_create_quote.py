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

    # Get the request ID to quote on
    request_id = os.getenv("RFQ_REQUEST_ID")

    if not request_id:
        # Find an active request to quote on
        print("No RFQ_REQUEST_ID provided, fetching active requests...")
        params = GetRfqRequestsParams(state="active", limit=1)
        response = client.rfq.get_rfq_requests(params)

        if response.get("data") and len(response["data"]) > 0:
            request = response["data"][0]
            request_id = request.get("requestId", request.get("request_id"))
            print(f"Found request: {request_id}")
            print(f"  Token: {request.get('token')}")
            print(f"  Side: {request.get('side')}")
            print(f"  Price: {request.get('price')}")
        else:
            print("No active requests found. Exiting.")
            return
    else:
        # Fetch the specific request
        print(f"Fetching request: {request_id}")
        params = GetRfqRequestsParams(request_ids=[request_id])
        response = client.rfq.get_rfq_requests(params)

        if not response.get("data") or len(response["data"]) == 0:
            print(f"Request {request_id} not found. Exiting.")
            return

        request = response["data"][0]

    # Determine quote parameters based on request
    # If the request is a BUY, the maker provides tokens and receives USDC
    # If the request is a SELL, the maker provides USDC and receives tokens
    side = request.get("side")
    token = request.get("token")
    size_in = request.get("sizeIn", request.get("size_in"))
    size_out = request.get("sizeOut", request.get("size_out"))

    if side == "BUY":
        # Requester wants to buy tokens (pay USDC, receive tokens)
        # Maker provides USDC (asset_in), receives tokens (asset_out)
        quote_params = CreateRfqQuoteParams(
            request_id=request_id,
            asset_in="0",  # Maker pays USDC
            asset_out=token,  # Maker receives tokens
            amount_in=size_out,  # Same USDC amount
            amount_out=size_in,  # Same token amount
        )
    else:
        # Requester wants to sell tokens (pay tokens, receive USDC)
        # Maker provides tokens (asset_in), receives USDC (asset_out)
        quote_params = CreateRfqQuoteParams(
            request_id=request_id,
            asset_in=token,  # Maker pays tokens
            asset_out="0",  # Maker receives USDC
            amount_in=size_out,  # Token amount
            amount_out=size_in,  # USDC amount
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
