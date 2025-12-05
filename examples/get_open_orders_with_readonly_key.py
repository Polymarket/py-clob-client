import os

import httpx
from dotenv import load_dotenv

from py_clob_client.endpoints import ORDERS


load_dotenv()


def main():
    host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")

    # Replace with your address and readonly API key
    address = os.getenv("POLY_ADDRESS", "0xc68576124eC1fF645F81a560E14003C8deF2e8fb")
    readonly_api_key = os.getenv("CLOB_READONLY_API_KEY", "019aee85-4ea1-79cd-a287-8508f21209a2")

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
        follow_redirects=True,
    )
    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Error {response.status_code}: {response.text}")
    print("Done!")


main()
