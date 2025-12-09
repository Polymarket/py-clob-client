import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.rfq import CreateRfqQuoteParams
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

    # Create a quote for an RFQ request
    quote_params = CreateRfqQuoteParams(
        request_id="0xaaaa",
        asset_in="0",  # Maker receives USDC
        asset_out="71321045679252212594626385532706912750332728571942532289631379312455583992563",
        amount_in="50000000",
        amount_out="100000000",
    )

    resp = client.rfq.create_rfq_quote(quote_params)
    print(resp)
    print("Done!")


main()
