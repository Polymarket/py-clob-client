import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.rfq import RfqUserOrder
from py_clob_client.order_builder.constants import BUY
from py_clob_client.constants import AMOY
from dotenv import load_dotenv

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

    # Create an RFQ request to BUY 100 tokens at $0.50 each
    user_order = RfqUserOrder(
        token_id="71321045679252212594626385532706912750332728571942532289631379312455583992563",
        price=0.50,
        side=BUY,
        size=100.0,
    )

    resp = client.rfq.create_rfq_request(user_order)
    print(resp)
    print("Done!")


main()
