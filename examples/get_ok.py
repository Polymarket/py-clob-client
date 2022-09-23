from py_clob_client.client import ClobClient


def main():
    host = "http://localhost:8080"
    client = ClobClient(host)

    print(client.get_ok())

    pass


main()
