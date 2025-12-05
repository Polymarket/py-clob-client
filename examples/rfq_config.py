"""
Example: Get RFQ configuration

This script demonstrates how to fetch the RFQ system configuration.
"""

import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
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

    print("Fetching RFQ configuration...")

    try:
        config = client.rfq.rfq_config()
        print(f"\nRFQ Configuration:")
        print(f"{config}")
    except Exception as e:
        print(f"\nError fetching RFQ config: {e}")

    print("\nDone!")


if __name__ == "__main__":
    main()
