import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, BalanceAllowanceParams, AssetType
from dotenv import load_dotenv
from py_clob_client.constants import AMOY

load_dotenv()


def main():
    host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    chain_id = AMOY
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    # USDC
    client.update_balance_allowance(
        params=BalanceAllowanceParams(asset_type=AssetType.COLLATERAL)
    )

    # YES
    client.update_balance_allowance(
        params=BalanceAllowanceParams(
            asset_type=AssetType.CONDITIONAL,
            token_id="52114319501245915516055106046884209969926127482827954674443846427813813222426",
        )
    )

    # NO
    client.update_balance_allowance(
        params=BalanceAllowanceParams(
            asset_type=AssetType.CONDITIONAL,
            token_id="71321045679252212594626385532706912750332728571942532289631379312455583992563",
        )
    )


main()
