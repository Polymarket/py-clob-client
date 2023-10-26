import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, BalanceAllowanceParams, AssetType
from dotenv import load_dotenv
from py_clob_client.constants import MUMBAI

load_dotenv()


def main():
    host = "http://localhost:8080"
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    chain_id = MUMBAI
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    collateral = client.get_balance_allowance(
        params=BalanceAllowanceParams(asset_type=AssetType.COLLATERAL)
    )
    print(collateral)

    yes = client.get_balance_allowance(
        params=BalanceAllowanceParams(
            asset_type=AssetType.CONDITIONAL,
            token_id="1343197538147866997676250008839231694243646439454152539053893078719042421992",
        )
    )
    print(yes)

    no = client.get_balance_allowance(
        params=BalanceAllowanceParams(asset_type=AssetType.CONDITIONAL),
        token_id="16678291189211314787145083999015737376658799626183230671758641503291735614088",
    )
    print(no)


main()
