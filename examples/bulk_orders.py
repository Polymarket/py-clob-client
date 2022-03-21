import os
import json

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, LimitOrderArgs, MarketOrderArgs
from dotenv import load_dotenv

from py_clob_client.orders.constants import BUY, LIMIT


load_dotenv()

def main():
    host = os.getenv("API_URL")
    key = os.getenv("PK")
    creds = ApiCreds(api_key=os.getenv("CLOB_API_KEY"), api_secret=os.getenv("CLOB_SECRET"), api_passphrase=os.getenv("CLOB_PASS_PHRASE"))
    chain_id = int(os.getenv("CHAIN_ID"))
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)
    f = open(os.getenv("BULK_ORDERS_FILE"))
    data = json.load(f)
    num_orders = len(data['orders'])
 
    for ix, order in enumerate(data['orders']):
        print(f'Processing order {ix+1} of {num_orders}...')
        if order['type'] == LIMIT:
            order_args = LimitOrderArgs(
                price=order['price'],
                size=order['size'],
                side=order['side'],
                token_id=order['token_id']
            )
            lim_order = client.create_limit_order(order_args)
            resp = client.post_order(lim_order)
            print(resp)
        else:
            order_args = MarketOrderArgs(
                size=order['size'],
                side=order['side'],
                token_id=order['token_id']
            )
            mkt_order = client.create_market_order(order_args)
            resp = client.post_order(mkt_order)
            print(resp)
 
    f.close()

main()
