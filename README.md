## py-clob-client

<a href='https://pypi.org/project/py-clob-client'>
    <img src='https://img.shields.io/pypi/v/py-clob-client.svg' alt='PyPI'/>
</a>

Python client for the Polymarket CLOB

### Installation

`pip install py-clob-client`

Intended for use with Python 3.9

### Usage

```py
host = "http://localhost:8080"
key = os.getenv("PK")
creds = ApiCreds(api_key=os.getenv("CLOB_API_KEY"), api_secret=os.getenv("CLOB_SECRET"), api_passphrase=os.getenv("CLOB_PASS_PHRASE"))
chain_id = 80001
client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

# Create and sign an order buying 100 YES tokens for 0.50c each
resp = client.create_and_post_order(OrderArgs(
    price=0.50,
    size=100.0,
    side=BUY,
    token_id="16678291189211314787145083999015737376658799626183230671758641503291735614088"
))

print(resp)
```

See [examples](examples/) for more
