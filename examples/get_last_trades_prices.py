import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import BookParams
from dotenv import load_dotenv
from pprint import pprint

from py_clob_client.constants import AMOY


load_dotenv()


def main():
    host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
    key = os.getenv("PK")
    chain_id = AMOY
    client = ClobClient(host, key=key, chain_id=chain_id)

    resp = client.get_last_trades_prices(
        params=[
            BookParams(
                token_id="71321045679252212594626385532706912750332728571942532289631379312455583992563"
            ),
            BookParams(
                token_id="52114319501245915516055106046884209969926127482827954674443846427813813222426"
            ),
        ]
    )
    pprint(resp)
    print("Done!")


main()
