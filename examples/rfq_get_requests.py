"""
Example: Get RFQ requests

This script demonstrates how to fetch RFQ requests with various filters.
"""

import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.rfq import GetRfqRequestsParams
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

    # Get all active RFQ requests
    print("Fetching active RFQ requests...")
    params = GetRfqRequestsParams(
        state="active",
        limit=10,
    )
    response = client.rfq.get_rfq_requests(params)

    if "data" in response:
        requests = response["data"]
        print(f"Found {len(requests)} active requests\n")

        for req in requests:
            print(f"Request ID: {req.get('requestId', req.get('request_id'))}")
            print(f"  Token: {req.get('token')}")
            print(f"  Side: {req.get('side')}")
            print(f"  Price: {req.get('price')}")
            print(f"  Size In: {req.get('sizeIn', req.get('size_in'))}")
            print(f"  Size Out: {req.get('sizeOut', req.get('size_out'))}")
            print(f"  State: {req.get('state')}")
            print()
    else:
        print(f"Response: {response}")

    # Get requests by specific IDs
    request_id = os.getenv("RFQ_REQUEST_ID")
    if request_id:
        print(f"\nFetching specific request: {request_id}")
        params = GetRfqRequestsParams(request_ids=[request_id])
        response = client.rfq.get_rfq_requests(params)
        print(f"Response: {response}")

    print("\nDone!")


if __name__ == "__main__":
    main()
