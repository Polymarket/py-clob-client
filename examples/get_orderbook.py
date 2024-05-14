from py_clob_client.client import ClobClient


def main():
    host = "http://localhost:8080"
    client = ClobClient(host)

    orderbook = client.get_order_book(
        "71321045679252212594626385532706912750332728571942532289631379312455583992563"
    )
    print("orderbook", orderbook)

    hash = client.get_order_book_hash(orderbook)
    print("orderbook hash", hash)


main()
