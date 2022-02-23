from py_clob_client.client import ClobClient

def main():
    host = "http://localhost:8080"
    key = "0x"
    client = ClobClient(host, key=key, chain_id=42)

    print(client.create_api_key())


main()