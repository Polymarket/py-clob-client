## py-clob-client

<a href='https://pypi.org/project/py-clob-client'>
    <img src='https://img.shields.io/pypi/v/py-clob-client.svg' alt='PyPI'/>
</a>

Python client for the Polymarket CLOB. Full API documentation can be found [here](https://polymarket.github.io/slate-docs/#introduction). 

### Installation

`pip install py-clob-client`

Intended for use with Python 3.9

### Requisites

#### Allowances

The correct token allowances must be set before orders can be placed. The following mainnet (Polygon) allowances should be set by the funding (maker) address. For testnet addresses and additional documentation please refer to the [API documentation](https://polymarket.github.io/slate-docs/#introduction).

|                   token(s)                   |                   spender                    |                            description                            |
| :------------------------------------------: | :------------------------------------------: | :---------------------------------------------------------------: |
| `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` | `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` |        allow the exchange contract to transfer user's usdc        |
| `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045` | `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` | allow the exchange contract to transfer user's conditional tokens |

See [this gist](https://gist.github.com/L-Kov/18d976850078bf1131c139e4150a922d) for a an example of how to set these allowances for an account using python. 

### Usage

```py
import os
from py_clob_client.constants import POLYGON
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY

host = "https://clob.polymarket.com"
key = os.getenv("PK")
chain_id = POLYGON

# Create CLOB client and get/set API credentials
client = ClobClient(host, key=key, chain_id=chain_id)
client.set_api_creds(client.create_or_derive_api_creds())

# Create and sign an order buying 100 YES tokens for 0.50c each
resp = client.create_and_post_order(OrderArgs(
    price=0.50,
    size=100.0,
    side=BUY,
    token_id="16678291189211314787145083999015737376658799626183230671758641503291735614088"
))

print(resp)
```

**See [examples](examples/) for more.**
