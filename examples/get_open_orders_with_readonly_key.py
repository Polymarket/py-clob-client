import os

import httpx
from dotenv import load_dotenv

from py_clob_client.endpoints import ORDERS


load_dotenv()


def main():
    host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
    address = os.getenv("POLY_ADDRESS")

    # Replace with your readonly API key from create_readonly_api_key
    readonly_api_key = os.getenv("CLOB_READONLY_API_KEY", "your-readonly-api-key-here")

    # Get all open orders for the address
    response = httpx.get(
        f"{host}{ORDERS}",
        headers={
            "POLY_READONLY_API_KEY": readonly_api_key,
            "POLY_ADDRESS": address,
            "Content-Type": "application/json",
        },
        params={
            "maker_address": address,
        },
    )
    print(response.json())
    print("Done!")


main()
