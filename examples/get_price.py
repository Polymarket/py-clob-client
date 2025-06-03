from py_clob_client.client import ClobClient
from py_clob_client.clob_types import BookParams


def main():
    host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
    client = ClobClient(host)

    resp = client.get_price(
        "71321045679252212594626385532706912750332728571942532289631379312455583992563",
        "BUY",
    )
    print(resp)
    print("Done!")


main()
