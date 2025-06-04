import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, TradeParams
from dotenv import load_dotenv
from pprint import pprint

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

    resp = client.get_trades(
        TradeParams(
            maker_address=client.get_address(),
            market="0x5f65177b394277fd294cd75650044e32ba009a95022d88a0c1d565897d72f8f1",
        )
    )
    pprint(resp)
    print("Done!")


main()
