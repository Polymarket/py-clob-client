## Bulk orders

### Usage

Create an `.env` file containing

```bash
PK=YOUR_WALLET_PRIVATE_KEY
CLOB_API_KEY=YOUR_CLOB_API_KEY
CLOB_SECRET=YOUR_CLOB_API_SECRET
CLOB_PASS_PHRASE=YOUR_CLOB_API_PASSPHRASE
BULK_ORDERS_FILE=orders.json
API_URL=https://clob-staging.polymarket.com
CHAIN_ID=80001
```

Create bulk orders file named `orders.json`.

```json
{
  "orders": [
    {
      "type": "limit",
      "price": 0.5,
      "side": "buy",
      "size": 2,
      "token_id": "16678291189211314787145083999015737376658799626183230671758641503291735614088"
    },
    {
      "type": "market",
      "side": "sell",
      "size": 10,
      "token_id": "16678291189211314787145083999015737376658799626183230671758641503291735614088"
    },
    {
      "type": "limit",
      "price": 0.5,
      "side": "buy",
      "size": 3,
      "token_id": "16678291189211314787145083999015737376658799626183230671758641503291735614088"
    }
  ]
}
```

Execute

```bash
python examples/bulk_orders.py
```
