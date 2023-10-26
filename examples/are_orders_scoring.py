import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrdersScoringParams
from dotenv import load_dotenv
from py_clob_client.constants import MUMBAI

load_dotenv()


def main():
    host = "http://localhost:8080"
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    chain_id = MUMBAI
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    scoring = client.are_orders_scoring(
        OrdersScoringParams(
            orderIds=[
                "0xb816482a5187a3d3db49cbaf6fe3ddf24f53e6c712b5a4bf5e01d0ec7b11dabc"
            ]
        )
    )
    print(scoring)
    print("Done!")


main()
