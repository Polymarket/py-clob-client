import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs
from dotenv import load_dotenv
from py_clob_client.constants import POLYGON

from py_clob_client.order_builder.constants import BUY


load_dotenv()


def main():
    host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
    key = os.getenv("PK")
    chain_id = POLYGON

    # Funder address - required for proxy/smart contract wallets
    # This is the address that holds your funds on Polymarket
    # For email/Magic wallets: your Polymarket profile address
    # For EOA wallets: can be the same as your signer address
    funder = os.getenv("FUNDER")

    # Signature type:
    # 0 = EOA (MetaMask, hardware wallet - direct private key control)
    # 1 = Email/Magic wallet (delegated signing)
    # 2 = Browser wallet proxy / Gnosis Safe
    signature_type = int(os.getenv("SIGNATURE_TYPE", "0"))

    client = ClobClient(
        host,
        key=key,
        chain_id=chain_id,
        signature_type=signature_type,
        funder=funder,
    )

    # Create or derive API credentials
    client.set_api_creds(client.create_or_derive_api_creds())

    # Create and sign a limit order buying 20 YES tokens at 0.50 each
    order_args = OrderArgs(
        price=0.50,
        size=20,
        side=BUY,
        token_id="71321045679252212594626385532706912750332728571942532289631379312455583992563",
    )
    signed_order = client.create_order(order_args)
    resp = client.post_order(signed_order)
    print(resp)
    print("Done!")


main()
