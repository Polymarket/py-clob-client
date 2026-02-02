"""
Minimal example: Fetch active Polymarket markets
"""

from polymarket.client import ClobClient


def main():
    client = ClobClient(
        host="https://clob.polymarket.com",
        key_id="YOUR_KEY",
        secret="YOUR_SECRET",
    )

    markets = client.get_markets(active=True)

    for market in markets[:5]:
        print(market["question"], market["market_id"])


if __name__ == "__main__":
    main()
