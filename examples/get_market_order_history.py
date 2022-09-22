import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, FilterParams
from dotenv import load_dotenv
from pprint import pprint


load_dotenv()


def main():
    host = "http://localhost:8080"
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    chain_id = 80001
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    resp = client.get_market_order_history(
        FilterParams(
            max=1,
            market="16678291189211314787145083999015737376658799626183230671758641503291735614088",
        )
    )
    pprint(resp)
    print("Done!")


main()
