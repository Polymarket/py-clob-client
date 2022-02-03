from py_clob_client.client import ClobClient

def main():
    host = "http://localhost:8080"
    key = "0x"
    client = ClobClient(host, key=key)

    print(client.create_api_key())


main()