import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs
from dotenv import load_dotenv
from py_clob_client.constants import AMOY
from py_clob_client.clob_types import (OrderType)
from py_clob_client.order_builder.constants import BUY, SELL


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
    order_args = OrderArgs(
        price=0.4,
        size=5,
        side=BUY,
        token_id="102200530570339469387764365697342150521708074903735836831685780223982723092914",
    )
    order = client.create_order(order_args)
    resp = client.post_order(order, orderType=OrderType.GTC, post_only=True)
    print(resp)
    print("Done!")


main()
