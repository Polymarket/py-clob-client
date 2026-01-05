import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs
from dotenv import load_dotenv
from py_clob_client.constants import AMOY

from py_clob_client.order_builder.constants import BUY


load_dotenv()


def main():
    host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    chain_id = int(os.getenv("CHAIN_ID", AMOY))
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    # Create and sign a limit order buying 100 YES tokens for 0.0005 each
    order_args = OrderArgs(
        price=0.0005,
        size=20,
        side=BUY,
        token_id="71321045679252212594626385532706912750332728571942532289631379312455583992563",
    )
    signed_order = client.create_order(order_args)
    resp = client.post_order(signed_order)
    print(resp)
    print("Done!")


main()
