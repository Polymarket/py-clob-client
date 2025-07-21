from py_clob_client.client import ClobClient


def main():
    host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
    client = ClobClient(host)

    print(client.get_server_time())


main()
