import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs
from dotenv import load_dotenv
from py_clob_client.constants import POLYGON

from py_clob_client.order_builder.constants import BUY
from py_builder_signing_sdk.config import BuilderConfig, BuilderApiKeyCreds

load_dotenv()


def main():
    host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    chain_id = POLYGON
    builder_config = BuilderConfig(
        local_builder_creds=BuilderApiKeyCreds(
            key=os.getenv("BUILDER_API_KEY"),
            secret=os.getenv("BUILDER_SECRET"),
            passphrase=os.getenv("BUILDER_PASS_PHRASE"),
        )
    )
    client = ClobClient(
        host, key=key, chain_id=chain_id, creds=creds, builder_config=builder_config
    )

    order_args = OrderArgs(
        price=0.06,
        size=20,
        side=BUY,
        token_id="104173557214744537570424345347209544585775842950109756851652855913015295701992",
    )
    signed_order = client.create_order(order_args)
    resp = client.post_order(signed_order)
    print(resp)
    print("Done!")


main()
