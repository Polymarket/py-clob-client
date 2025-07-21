import os

from py_clob_client.client import ClobClient
from dotenv import load_dotenv
from pprint import pprint

from py_clob_client.constants import AMOY


load_dotenv()


def main():
    host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
    key = os.getenv("PK")
    chain_id = AMOY
    client = ClobClient(host, key=key, chain_id=chain_id)

    resp = client.get_last_trade_price(
        "71321045679252212594626385532706912750332728571942532289631379312455583992563"
    )
    pprint(resp)
    print("Done!")


main()
