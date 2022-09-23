from py_clob_client.client import ClobClient


def main():
    host = "http://localhost:8080"
    client = ClobClient(host)

    print(
        client.get_order_book(
            "16678291189211314787145083999015737376658799626183230671758641503291735614088"
        )
    )


main()
