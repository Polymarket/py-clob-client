import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import MarketOrderArgs, OrderType
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

    # Create a market buy order for the equivalent of 100 USDC at the market price
    # Note: For BUY orders, 'amount' is in USDC ($$$)
    #       For SELL orders, 'amount' is in shares
    order_args = MarketOrderArgs(
        token_id="71321045679252212594626385532706912750332728571942532289631379312455583992563",
        amount=100,  # $$$ (USDC amount for BUY orders)
        side=BUY,
    )
    signed_order = client.create_market_order(order_args)
    resp = client.post_order(signed_order, orderType=OrderType.FOK)
    print(resp)
    print("Done!")


main()
