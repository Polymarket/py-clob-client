import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OpenOrderParams
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
    chain_id = AMOY
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    resp = client.get_orders(
        OpenOrderParams(
            market="0x37a6a2dd9f3469495d9ec2467b0a764c5905371a294ce544bc3b2c944eb3e84a",
        )
    )
    print(resp)
    print("Done!")


main()
