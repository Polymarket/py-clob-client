import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs, PostOrdersArgs, OrderType
from dotenv import load_dotenv
from py_clob_client.constants import AMOY

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

    resp = client.post_orders(
        [
            PostOrdersArgs(
                # Create and sign a limit order buying 100 YES tokens for 0.50 each
                order=client.create_order(
                    OrderArgs(
                        price=0.5,
                        size=100,
                        side=BUY,
                        token_id="71321045679252212594626385532706912750332728571942532289631379312455583992563",
                    )
                ),
                orderType=OrderType.GTC,  # Good 'Til Cancelled
                postOnly=False,
            ),
            PostOrdersArgs(
                # Create and sign a limit order selling 200 NO tokens for 0.25 each
                order=client.create_order(
                    OrderArgs(
                        price=0.25,
                        size=200,
                        side=SELL,
                        token_id="52114319501245915516055106046884209969926127482827954674443846427813813222426",
                    )
                ),
                orderType=OrderType.GTC,  # Good 'Til Cancelled
                postOnly=False, # Defaults to false, can be set to true to avoid matching on post
            ),
        ]
    )
    print(resp)
    print("Done!")


main()
