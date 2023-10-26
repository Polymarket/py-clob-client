import os

from py_clob_client.client import ClobClient
from py_clob_client.model.clob import ApiCreds
from dotenv import load_dotenv
from py_clob_client.constants import MUMBAI


load_dotenv()


def main():
    host = "http://localhost:8080"
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    chain_id = MUMBAI
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    resp = client.get_midpoint(
        "16678291189211314787145083999015737376658799626183230671758641503291735614088"
    )
    # {'mid': '0.55'}
    print(resp)
    print("Done!")


main()
