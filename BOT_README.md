# Polymarket Directional Trading Bot

A simple, directional trading bot for Polymarket with HTTP control API.

## Architecture

```
main.py                 # Entry point: starts FastAPI + trading loop
bot/
  state.py              # Shared mutable state (paused, mode, risk limits)
  execution.py          # Wrapper around py-clob-client
  strategy.py           # Your trading logic (customize this!)
```

## Requirements

- Python 3.10+
- Polymarket account with API credentials
- Funded wallet on Polygon

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `POLY_PRIVATE_KEY` | Yes | Your wallet private key |
| `POLY_API_KEY` | Yes | Polymarket API key |
| `POLY_API_SECRET` | Yes | Polymarket API secret |
| `POLY_API_PASSPHRASE` | Yes | Polymarket API passphrase |
| `BOT_TOKEN` | Yes | Secret token for API authentication |
| `PORT` | No | HTTP server port (default: 8000) |
| `POLY_HOST` | No | CLOB host (default: https://clob.polymarket.com) |
| `LOOP_INTERVAL` | No | Trading loop interval in seconds (default: 60) |

### Generating BOT_TOKEN

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Getting Polymarket API Credentials

1. Go to https://polymarket.com
2. Connect your wallet
3. Go to Settings > API Keys
4. Create a new API key (store the credentials safely!)

---

## Local Development (GitHub Codespaces)

### 1. Fork and Open in Codespaces

1. Fork this repository to your GitHub account
2. Click "Code" > "Codespaces" > "Create codespace on main"
3. Wait for the environment to build

### 2. Install Dependencies

```bash
pip install -r bot_requirements.txt
pip install -e .
```

### 3. Set Environment Variables

Create a `.env` file (never commit this!):

```bash
cat > .env << 'EOF'
POLY_PRIVATE_KEY=your_private_key_here
POLY_API_KEY=your_api_key_here
POLY_API_SECRET=your_api_secret_here
POLY_API_PASSPHRASE=your_passphrase_here
BOT_TOKEN=your_generated_bot_token_here
PORT=8000
EOF
```

Load the environment:

```bash
export $(cat .env | xargs)
```

### 4. Run the Bot

```bash
python main.py
```

### 5. Test the API

In another terminal:

```bash
# Health check (no auth)
curl http://localhost:8000/health

# Get status (requires auth)
curl -H "Authorization: Bearer $BOT_TOKEN" http://localhost:8000/status
```

---

## Railway Deployment

### 1. Create Railway Project

1. Go to https://railway.app
2. Create a new project
3. Choose "Deploy from GitHub repo"
4. Select your forked repository

### 2. Configure Environment Variables

In Railway dashboard > Variables, add:

- `POLY_PRIVATE_KEY`
- `POLY_API_KEY`
- `POLY_API_SECRET`
- `POLY_API_PASSPHRASE`
- `BOT_TOKEN`

Railway automatically provides `PORT`.

### 3. Configure Start Command

In Settings > Deploy, set:

```
python main.py
```

### 4. Deploy

Railway will automatically deploy when you push to your repo.

### 5. Get Your Bot URL

Railway provides a public URL like: `https://your-project.up.railway.app`

---

## Control API

All POST endpoints require authentication:

```bash
-H "Authorization: Bearer YOUR_BOT_TOKEN"
```

### Endpoints

#### GET /health
Health check (no auth required).

```bash
curl https://your-bot.railway.app/health
```

#### GET /status
Get current bot status.

```bash
curl -H "Authorization: Bearer $BOT_TOKEN" \
  https://your-bot.railway.app/status
```

Response:
```json
{
  "paused": true,
  "mode": "paper",
  "uptime_seconds": 3600,
  "uptime_human": "1h 0m 0s",
  "last_command": "resume",
  "last_command_time": "2024-01-15T10:30:00",
  "last_trade_time": null,
  "risk_limits": {
    "max_order_size": 100.0,
    "max_exposure_per_market": 500.0
  },
  "usdc_balance": 1234.56
}
```

#### POST /pause
Pause the trading bot.

```bash
curl -X POST -H "Authorization: Bearer $BOT_TOKEN" \
  https://your-bot.railway.app/pause
```

#### POST /resume
Resume the trading bot.

```bash
curl -X POST -H "Authorization: Bearer $BOT_TOKEN" \
  https://your-bot.railway.app/resume
```

#### POST /mode/{paper|live}
Set trading mode.

```bash
# Paper trading (no real orders)
curl -X POST -H "Authorization: Bearer $BOT_TOKEN" \
  https://your-bot.railway.app/mode/paper

# Live trading (real orders!)
curl -X POST -H "Authorization: Bearer $BOT_TOKEN" \
  https://your-bot.railway.app/mode/live
```

#### POST /risk
Update risk limits.

```bash
curl -X POST -H "Authorization: Bearer $BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"max_order_size": 50, "max_exposure_per_market": 200}' \
  https://your-bot.railway.app/risk
```

#### GET /markets
Get summary of watched markets.

```bash
curl -H "Authorization: Bearer $BOT_TOKEN" \
  https://your-bot.railway.app/markets
```

#### POST /cancel-all
Cancel all open orders.

```bash
curl -X POST -H "Authorization: Bearer $BOT_TOKEN" \
  https://your-bot.railway.app/cancel-all
```

---

## Quick Reference: Phone Terminal Commands

Save your bot URL and token:

```bash
export BOT_URL="https://your-bot.railway.app"
export BOT_TOKEN="your_token_here"
```

Common operations:

```bash
# Check status
curl -s -H "Authorization: Bearer $BOT_TOKEN" $BOT_URL/status | jq

# Pause bot
curl -s -X POST -H "Authorization: Bearer $BOT_TOKEN" $BOT_URL/pause | jq

# Resume bot
curl -s -X POST -H "Authorization: Bearer $BOT_TOKEN" $BOT_URL/resume | jq

# Switch to paper mode
curl -s -X POST -H "Authorization: Bearer $BOT_TOKEN" $BOT_URL/mode/paper | jq

# Switch to live mode (careful!)
curl -s -X POST -H "Authorization: Bearer $BOT_TOKEN" $BOT_URL/mode/live | jq

# Emergency: cancel all orders
curl -s -X POST -H "Authorization: Bearer $BOT_TOKEN" $BOT_URL/cancel-all | jq
```

---

## Customizing the Strategy

Edit `bot/strategy.py` to implement your trading logic:

1. Add markets to `WATCHED_MARKETS` list
2. Implement `generate_signal()` function
3. The bot will call this function every `LOOP_INTERVAL` seconds

Example:

```python
WATCHED_MARKETS = [
    MarketConfig(
        condition_id="0x...",
        token_id_yes="12345...",
        token_id_no="67890...",
        name="Will BTC reach $100k?"
    ),
]

def generate_signal() -> Optional[Signal]:
    for market in WATCHED_MARKETS:
        midpoint = engine.get_midpoint(market.token_id_yes)

        # Your logic here
        if midpoint < 0.30:
            return Signal(
                token_id=market.token_id_yes,
                side="BUY",
                price=midpoint + 0.01,
                size=10,
                reason="Price below threshold",
                confidence=0.7,
            )

    return None
```

---

## Safety Features

1. **Starts paused**: Bot starts in paused state
2. **Paper mode default**: Starts in paper mode
3. **Risk limits**: Max order size and exposure enforced
4. **Token auth**: All control endpoints require authentication
5. **Sanity checks**: Price must be 0-1, size must be positive

---

## Security Notes

- Never commit `.env` files or secrets
- Use strong, random `BOT_TOKEN` values
- Keep your private key secure
- Consider using a dedicated trading wallet with limited funds
- Monitor your bot's activity regularly
