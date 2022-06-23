import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, LimitOrderArgs, MarketOrderArgs
from dotenv import load_dotenv

from py_clob_client.orders.constants import BUY, SELL


load_dotenv()

def main():
    host = "http://localhost:8080"
    key = os.getenv("PK")
    creds = ApiCreds(api_key=os.getenv("CLOB_API_KEY"), api_secret=os.getenv("CLOB_SECRET"), api_passphrase=os.getenv("CLOB_PASS_PHRASE"))
    chain_id = 80001
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)
    no_token = "1343197538147866997676250008839231694243646439454152539053893078719042421992"

    # Limit order
    order_args = LimitOrderArgs(
        price=0.50,
        size=100.0,
        side=BUY,
        token_id=no_token
    )
    lim_order = client.create_limit_order(order_args)
    client.post_order(lim_order)

    # FOK, error expected
    fok_order_args = MarketOrderArgs(
        size=200.0,
        side=SELL,
        token_id=no_token,
        time_in_foce="FOK"
    )
    fok_mkt_order = client.create_market_order(fok_order_args)
    print("FOK market order")
    print(client.post_order(fok_mkt_order))

    # IOC, match expected
    ioc_order_args = MarketOrderArgs(
        size=200.0,
        side=SELL,
        token_id=no_token,
        time_in_foce="IOC"
    )
    ioc_mkt_order = client.create_market_order(ioc_order_args)
    print("IOC market order")
    print(client.post_order(ioc_mkt_order))


main()