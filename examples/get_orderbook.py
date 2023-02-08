from py_clob_client.client import ClobClient


def main():
    host = "http://localhost:8080"
    client = ClobClient(host)

    orderbook = client.get_order_book(
        "16678291189211314787145083999015737376658799626183230671758641503291735614088"
    )
    print("orderbook", orderbook)

    hash = client.get_order_book_hash(orderbook)
    print("orderbook hash", hash)


main()
