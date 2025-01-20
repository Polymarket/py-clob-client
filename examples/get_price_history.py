from py_clob_client.client import ClobClient


def main():
    host = "http://localhost:8080"
    client = ClobClient(host)

    resp = client.get_price_history_with_interval(
        "5114173491195416254365602929074381343823182276653657249022440867189120977342",
        "1d",
        60,
    )
    print(resp)
    print("Done!")


main()
