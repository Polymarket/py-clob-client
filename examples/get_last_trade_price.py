import os

from py_clob_client.client import ClobClient
from dotenv import load_dotenv
from pprint import pprint

from py_clob_client.constants import AMOY


load_dotenv()


def main():
    host = "http://localhost:8080"
    key = os.getenv("PK")
    chain_id = AMOY
    client = ClobClient(host, key=key, chain_id=chain_id)

    resp = client.get_last_trade_price(
        "16678291189211314787145083999015737376658799626183230671758641503291735614088"
    )
    pprint(resp)
    print("Done!")


main()
