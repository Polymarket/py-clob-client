import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.rfq import RfqUserQuote
from py_clob_client.order_builder.constants import SELL
from py_clob_client.constants import AMOY
from dotenv import load_dotenv

load_dotenv()


def main():
    host = os.getenv("CLOB_API_URL", "https://clob-staging.polymarket.com/")
    chain_id = os.getenv("CHAIN_ID", AMOY)
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    # Create a quote for an RFQ request to SELL 100 tokens at $0.50 each
    user_quote = RfqUserQuote(
        request_id="0xaaaa",
        price=0.50,
        side=SELL,
        size=100.0,
    )

    resp = client.rfq.create_rfq_quote(user_quote)
    print(resp)
    print("Done!")


main()
