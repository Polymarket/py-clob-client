import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, PartialCreateOrderOptions
from py_clob_client.rfq import RfqUserRequest
from py_clob_client.order_builder.constants import BUY
from py_clob_client.constants import AMOY
from dotenv import load_dotenv

load_dotenv()


def main():
    host = os.getenv("CLOB_API_URL", "https://clob-staging.polymarket.com/")
    chain_id = int(os.getenv("CHAIN_ID", AMOY))
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    # Create an RFQ request to BUY 100 tokens at $0.50 each
    user_request = RfqUserRequest(
        token_id="34097058504275310827233323421517291090691602969494795225921954353603704046623",
        price=0.50,
        side=BUY,
        size=40.0,
    )

    resp = client.rfq.create_rfq_request(user_request, options=PartialCreateOrderOptions(tick_size=0.01))
    print(resp)
    print("Done!")


main()
