from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYMARKET_HOST
from py_clob_client.credentials import Credentials


def main():
    creds = Credentials(
        api_key="YOUR_API_KEY",
        api_secret="YOUR_API_SECRET",
        api_passphrase="YOUR_API_PASSPHRASE",
    )

    client = ClobClient(
        host=POLYMARKET_HOST,
        key=creds.api_key,
        creds=creds,
    )

    next_cursor = None

    while True:
        response = client.get_markets(next_cursor=next_cursor)

        markets = response.get("data", [])
        for market in markets:
            print(market.get("question"))

        next_cursor = response.get("next_cursor")
        if not next_cursor:
            break


if __name__ == "__main__":
    main()
