import os
import time

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from dotenv import load_dotenv

from py_clob_client.constants import AMOY


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

    heartbeat_id = None
    while True:
        resp = client.post_heartbeat(heartbeat_id)
        print(resp)
        heartbeat_id = resp["heartbeat_id"]
        # Wait 5 seconds before sending the next heartbeat
        time.sleep(5)
    # Example output on invalid heartbeat ID once heartbeats started:
    # PolyApiException[status_code=400, error_message={"error":"Invalid Heartbeat ID","heartbeat_id":"7f335bb3-36cb-433d-b8ff-4f9a2233d833"}




main()
