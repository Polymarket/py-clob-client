from dotenv import load_dotenv
import os

from py_clob_client.client import ClobClient

load_dotenv()


def main():
    host = "http://localhost:8080"
    key = os.getenv("PK")
    chain_id = 80001
    client = ClobClient(host, key=key, chain_id=chain_id)

    print(client.create_api_key())


main()
