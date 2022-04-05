import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, LimitOrderArgs, MarketOrderArgs
from dotenv import load_dotenv
from pprint import pprint
from py_clob_client.orders.constants import BUY

load_dotenv()

def main():
    host = "http://localhost:8080"
    key = os.getenv("PK")
    creds = ApiCreds(api_key=os.getenv("CLOB_API_KEY"), api_secret=os.getenv("CLOB_SECRET"), api_passphrase=os.getenv("CLOB_PASS_PHRASE"))
    chain_id = 80001
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    # Create and sign a market order, using 100 USDC size to buy as many tokens as possible
    # Note: Size in market buy is the COLLATERAL size used to initiate the buy
    # While in a market sell, size is the amount of YES/NO tokens used to initiate the sell
    order_args = MarketOrderArgs(
        size=100.0,
        side=BUY,
        token_id="16678291189211314787145083999015737376658799626183230671758641503291735614088"
    )
    mkt_order = client.create_market_order(order_args)
    resp = client.post_order(mkt_order)
    pprint(resp)
    print("Done!")


main()