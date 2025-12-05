"""
Example: Create an RFQ request (Taker side)

This script demonstrates how a taker can create an RFQ request
to buy or sell tokens at a specified price.
"""

import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.rfq import RfqUserOrder
from py_clob_client.order_builder.constants import BUY, SELL
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

    # Token ID for the market you want to trade
    token_id = os.getenv(
        "TOKEN_ID",
        "34097058504275310827233323421517291090691602969494795225921954353603704046623",
    )

    # Create an RFQ request to BUY 100 tokens at $0.50 each
    user_order = RfqUserOrder(
        token_id=token_id,
        price=0.50,
        side=BUY,
        size=100.0,
    )

    # Create and post the RFQ request
    print("Creating RFQ request...")
    response = client.rfq.create_rfq_request(user_order)

    print(f"Response: {response}")
    if "requestId" in response:
        print(f"\nRFQ Request created successfully!")
        print(f"Request ID: {response['requestId']}")
    else:
        print(f"\nFailed to create RFQ request")

    print("\nDone!")


if __name__ == "__main__":
    main()
