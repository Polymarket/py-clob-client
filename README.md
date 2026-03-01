# Polymarket Python CLOB Client

<a href='https://pypi.org/project/py-clob-client'>
    <img src='https://img.shields.io/pypi/v/py-clob-client.svg' alt='PyPI'/>
</a>

Python client for the Polymarket Central Limit Order Book (CLOB).

## Documentation

## Installation

```bash
# install from PyPI (Python 3.9>)
pip install py-clob-client
```
## Usage

The examples below are short and copy‑pasteable.

- What you need:
  - **Python 3.9+**
  - **Private key** that owns funds on Polymarket
  - Optional: a **proxy/funder address** if you use an email or smart‑contract wallet
  - Tip: store secrets in environment variables (e.g., with `.env`)

### Quickstart (read‑only)

```python
from py_clob_client.client import ClobClient

client = ClobClient("https://clob.polymarket.com")  # Level 0 (no auth)

ok = client.get_ok()
time = client.get_server_time()
print(ok, time)
```

### Start trading (EOA)

**Note**: If using MetaMask or hardware wallet, you must first set token allowances. See [Token Allowances section](#important-token-allowances-for-metamaskeoa-users) below.

```python
from py_clob_client.client import ClobClient

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137
PRIVATE_KEY = "<your-private-key>"
FUNDER = "<your-funder-address>"

client = ClobClient(
    HOST,  # The CLOB API endpoint
    key=PRIVATE_KEY,  # Your wallet's private key
    chain_id=CHAIN_ID,  # Polygon chain ID (137)
    signature_type=1,  # 1 for email/Magic wallet signatures
    funder=FUNDER  # Address that holds your funds
)
client.set_api_creds(client.create_or_derive_api_creds())
```

### Start trading (proxy wallet)

For email/Magic or browser wallet proxies, you need to specify two additional parameters. **Critical: The most common mistake is confusing which address goes in `key` vs `funder`.**

#### Signature Types
The **signature_type** parameter tells the system how to verify your signatures:

- `signature_type=0` (default): **EOA (Externally Owned Account)** - MetaMask, hardware wallets, any wallet where you directly control the private key
  - `key`: Your wallet's private key
  - `funder`: Your wallet's address (or omit - defaults to signer address)

- `signature_type=1`: **Polymarket Proxy** - Email/Magic wallets with Polymarket's proxy system  
  - `key`: Your wallet's private key (the one that controls the proxy)
  - `funder`: The proxy contract address (where your funds are held)

- `signature_type=2`: **Gnosis Safe Proxy** - 1-of-1 Gnosis Safe where you're the sole owner
  - `key`: **EOA private key that OWNS the Gnosis Safe** (not the Safe's address)
  - `funder`: **The Gnosis Safe contract address** (where your funds are held)

#### ⚠️ Common "Invalid Signature" Mistakes

**For signature_type=2 (Gnosis Safe):**
- ❌ **Wrong:** `key=safe_address, funder=eoa_address` 
- ✅ **Correct:** `key=eoa_private_key, funder=safe_address`

**The private key must be from the EOA that owns/controls the proxy, and funder must be the proxy contract address itself.**

#### Funder Address
The **funder address** is where your funds are actually held on Polymarket:
- **EOA mode:** Your wallet address (usually auto-detected)
- **Proxy mode:** The proxy contract address (not your EOA address)

#### Troubleshooting "Invalid Signature" Errors

If you get "invalid signature" errors with proxy mode:

1. **Verify your setup:**
   - For signature_type=2: private_key = EOA that owns the Safe, funder = Safe address
   - For signature_type=1: private_key = EOA that controls the proxy, funder = proxy address

2. **Test with EOA mode first:**
   ```python
   # Test that your private key works at all
   client = ClobClient(HOST, key=PRIVATE_KEY, chain_id=CHAIN_ID, signature_type=0)
   # Should get "not enough balance/allowance" error, not "invalid signature"
   ```

3. **Verify proxy ownership:**
   - For Gnosis Safe: Check that your EOA is the sole owner of the 1-of-1 Safe
   - For Polymarket proxy: Verify the proxy is properly linked to your EOA

```python
from py_clob_client.client import ClobClient

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137

# Example 1: Polymarket Proxy (signature_type=1)
EOA_PRIVATE_KEY = "<your-eoa-private-key>"  # EOA that controls the proxy
POLYMARKET_PROXY_ADDRESS = "<proxy-contract-address>"  # Where your funds are held

client = ClobClient(
    HOST,
    key=EOA_PRIVATE_KEY,  # The EOA key that controls the proxy
    chain_id=CHAIN_ID,
    signature_type=1,  # Polymarket proxy
    funder=POLYMARKET_PROXY_ADDRESS  # The proxy contract (not your EOA)
)

# Example 2: Gnosis Safe Proxy (signature_type=2)  
SAFE_OWNER_PRIVATE_KEY = "<eoa-owner-private-key>"  # EOA that owns the 1-of-1 Safe
GNOSIS_SAFE_ADDRESS = "<safe-contract-address>"  # Your Gnosis Safe address

client = ClobClient(
    HOST,
    key=SAFE_OWNER_PRIVATE_KEY,  # Private key of the Safe owner (EOA)
    chain_id=CHAIN_ID,
    signature_type=2,  # Gnosis Safe proxy
    funder=GNOSIS_SAFE_ADDRESS  # The Safe contract address
)

client.set_api_creds(client.create_or_derive_api_creds())
```

### Find markets, prices, and orderbooks

```python
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import BookParams

client = ClobClient("https://clob.polymarket.com")  # read-only

token_id = "<token-id>"  # Get a token ID: https://docs.polymarket.com/developers/gamma-markets-api/get-markets

mid = client.get_midpoint(token_id)
price = client.get_price(token_id, side="BUY")
book = client.get_order_book(token_id)
books = client.get_order_books([BookParams(token_id=token_id)])
print(mid, price, book.market, len(books))
```

### Place a market order (buy by $ amount)

**Note**: EOA/MetaMask users must set token allowances before trading. See [Token Allowances section](#important-token-allowances-for-metamaskeoa-users) below.

```python
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import MarketOrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137
PRIVATE_KEY = "<your-private-key>"
FUNDER = "<your-funder-address>"

client = ClobClient(
    HOST,  # The CLOB API endpoint
    key=PRIVATE_KEY,  # Your wallet's private key
    chain_id=CHAIN_ID,  # Polygon chain ID (137)
    signature_type=1,  # 1 for email/Magic wallet signatures
    funder=FUNDER  # Address that holds your funds
)
client.set_api_creds(client.create_or_derive_api_creds())

mo = MarketOrderArgs(token_id="<token-id>", amount=25.0, side=BUY, order_type=OrderType.FOK)  # Get a token ID: https://docs.polymarket.com/developers/gamma-markets-api/get-markets
signed = client.create_market_order(mo)
resp = client.post_order(signed, OrderType.FOK)
print(resp)
```

### Place a limit order (shares at a price)

**Note**: EOA/MetaMask users must set token allowances before trading. See [Token Allowances section](#important-token-allowances-for-metamaskeoa-users) below.

```python
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137
PRIVATE_KEY = "<your-private-key>"
FUNDER = "<your-funder-address>"

client = ClobClient(
    HOST,  # The CLOB API endpoint
    key=PRIVATE_KEY,  # Your wallet's private key
    chain_id=CHAIN_ID,  # Polygon chain ID (137)
    signature_type=1,  # 1 for email/Magic wallet signatures
    funder=FUNDER  # Address that holds your funds
)
client.set_api_creds(client.create_or_derive_api_creds())

order = OrderArgs(token_id="<token-id>", price=0.01, size=5.0, side=BUY)  # Get a token ID: https://docs.polymarket.com/developers/gamma-markets-api/get-markets
signed = client.create_order(order)
resp = client.post_order(signed, OrderType.GTC)
print(resp)
```

### Manage orders

**Note**: EOA/MetaMask users must set token allowances before trading. See [Token Allowances section](#important-token-allowances-for-metamaskeoa-users) below.

```python
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OpenOrderParams

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137
PRIVATE_KEY = "<your-private-key>"
FUNDER = "<your-funder-address>"

client = ClobClient(
    HOST,  # The CLOB API endpoint
    key=PRIVATE_KEY,  # Your wallet's private key
    chain_id=CHAIN_ID,  # Polygon chain ID (137)
    signature_type=1,  # 1 for email/Magic wallet signatures
    funder=FUNDER  # Address that holds your funds
)
client.set_api_creds(client.create_or_derive_api_creds())

open_orders = client.get_orders(OpenOrderParams())

order_id = open_orders[0]["id"] if open_orders else None
if order_id:
    client.cancel(order_id)

client.cancel_all()
```

### Markets (read‑only)

```python
from py_clob_client.client import ClobClient

client = ClobClient("https://clob.polymarket.com")
markets = client.get_simplified_markets()
print(markets["data"][:1])
```

### User trades (requires auth)

**Note**: EOA/MetaMask users must set token allowances before trading. See [Token Allowances section](#important-token-allowances-for-metamaskeoa-users) below.

```python
from py_clob_client.client import ClobClient

HOST = "https://clob.polymarket.com"
CHAIN_ID = 137
PRIVATE_KEY = "<your-private-key>"
FUNDER = "<your-funder-address>"

client = ClobClient(
    HOST,  # The CLOB API endpoint
    key=PRIVATE_KEY,  # Your wallet's private key
    chain_id=CHAIN_ID,  # Polygon chain ID (137)
    signature_type=1,  # 1 for email/Magic wallet signatures
    funder=FUNDER  # Address that holds your funds
)
client.set_api_creds(client.create_or_derive_api_creds())

last = client.get_last_trade_price("<token-id>")
trades = client.get_trades()
print(last, len(trades))
```

## Important: Token Allowances for MetaMask/EOA Users

### Do I need to set allowances?
- **Using email/Magic wallet?** No action needed - allowances are set automatically.
- **Using MetaMask or hardware wallet?** You need to set allowances before trading.

### What are allowances?
Think of allowances as permissions. Before Polymarket can move your funds to execute trades, you need to give the exchange contracts permission to access your USDC and conditional tokens.

### Quick Setup
You need to approve two types of tokens:
1. **USDC** (for deposits and trading)
2. **Conditional Tokens** (the outcome tokens you trade)

Each needs approval for the exchange contracts to work properly.

### Setting Allowances
Here's a simple breakdown of what needs to be approved:

**For USDC (your trading currency):**
- Token: `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`
- Approve for these contracts:
  - `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` (Main exchange)
  - `0xC5d563A36AE78145C45a50134d48A1215220f80a` (Neg risk markets)
  - `0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296` (Neg risk adapter)

**For Conditional Tokens (your outcome tokens):**
- Token: `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045`
- Approve for the same three contracts above

### Example Code
See [this Python example](https://gist.github.com/poly-rodr/44313920481de58d5a3f6d1f8226bd5e) for setting allowances programmatically.

**Pro tip**: You only need to set these once per wallet. After that, you can trade freely.

## Notes
- To discover token IDs, use the Markets API Explorer: [Get Markets](https://docs.polymarket.com/developers/gamma-markets-api/get-markets).
- Prices are in dollars from 0.00 to 1.00. Shares are whole or fractional units of the outcome token.

See [/example](/examples) for more.