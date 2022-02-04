import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, LimitOrderArgs
from dotenv import load_dotenv

from py_clob_client.orders.constants import BUY


load_dotenv()

def main():
    host = "http://localhost:8080"
    key = os.getenv("PK")
    creds = ApiCreds(api_key=os.getenv("CLOB_API_KEY"), api_secret=os.getenv("CLOB_SECRET"), api_passphrase=os.getenv("CLOB_PASS_PHRASE"))
    client = ClobClient(host, key=key, chain_id=42, creds=creds)

    """
    Create and sign a limit order buying 200 YES tokens for 0.50c each
    """
    order_args = LimitOrderArgs(
        price=0.50,
        size=200.0,
        side=BUY,
        token_id="52510691187011637615459506231858994888111914427496804500632984576264571090512"
    )
    lim_order = client.create_limit_order(order_args).json()
    print(lim_order)


main()