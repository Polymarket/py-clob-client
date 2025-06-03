from dotenv import load_dotenv
import os

from py_clob_client.client import ClobClient
from py_clob_client.constants import AMOY

load_dotenv()


def main():
    host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
    key = os.getenv("PK")
    chain_id = AMOY
    client = ClobClient(host, key=key, chain_id=chain_id)

    print(client.create_api_key())


main()
