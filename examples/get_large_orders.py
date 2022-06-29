import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, FilterParams
from dotenv import load_dotenv


load_dotenv()

def main():
    host = "http://localhost:8080"
    key = os.getenv("PK")
    creds = ApiCreds(api_key=os.getenv("CLOB_API_KEY"), api_secret=os.getenv("CLOB_SECRET"), api_passphrase=os.getenv("CLOB_PASS_PHRASE"))
    chain_id = 80001
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    resp = client.get_large_orders(FilterParams(min_value="1000"))
    print(resp)
    print("Done!")


main()