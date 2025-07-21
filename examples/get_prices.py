from py_clob_client.client import ClobClient
from py_clob_client.clob_types import BookParams


def main():
    host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
    client = ClobClient(host)

    resp = client.get_prices(
        params=[
            BookParams(
                token_id="71321045679252212594626385532706912750332728571942532289631379312455583992563",
                side="BUY",
            ),
            BookParams(
                token_id="71321045679252212594626385532706912750332728571942532289631379312455583992563",
                side="SELL",
            ),
            BookParams(
                token_id="52114319501245915516055106046884209969926127482827954674443846427813813222426",
                side="BUY",
            ),
            BookParams(
                token_id="52114319501245915516055106046884209969926127482827954674443846427813813222426",
                side="SELL",
            ),
        ]
    )
    print(resp)
    print("Done!")


main()
