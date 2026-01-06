from py_clob_client.client import ClobClient
import os
from dotenv import load_dotenv

load_dotenv()


def main():
    host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
    client = ClobClient(host)

    orderbook = client.get_order_book(
        "34097058504275310827233323421517291090691602969494795225921954353603704046623"
    )
    print("orderbook", orderbook)

    hash = client.get_order_book_hash(orderbook)
    print("orderbook hash", hash)


main()
