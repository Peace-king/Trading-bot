# Binance Futures Testnet Trading Bot

A clean, structured Python CLI application for placing orders on the **Binance Futures Testnet (USDT-M)**.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package exports
│   ├── client.py            # Binance REST client (auth, signing, HTTP)
│   ├── orders.py            # Order placement logic + output formatting
│   ├── validators.py        # Input validation
│   └── logging_config.py   # File + console logging setup
├── cli.py                   # CLI entry point (argparse)
├── .env.example             # Credential template
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Register a Testnet Account

Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com), register, and generate API credentials under **API Management**.

### 2. Clone / Download

```bash
git clone <your-repo-url>
cd trading_bot
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Credentials

```bash
cp .env.example .env
# Edit .env and paste your API key and secret
```

---

## Usage

### Check Connectivity

```bash
python cli.py ping
```

### Place a MARKET Order

```bash
python cli.py place-order \
  --symbol BTCUSDT \
  --side BUY \
  --type MARKET \
  --quantity 0.001
```

### Place a LIMIT Order

```bash
python cli.py place-order \
  --symbol BTCUSDT \
  --side SELL \
  --type LIMIT \
  --quantity 0.001 \
  --price 90000
```

### Place a STOP_MARKET Order (Bonus)

```bash
python cli.py place-order \
  --symbol BTCUSDT \
  --side BUY \
  --type STOP_MARKET \
  --quantity 0.001 \
  --stop-price 85000
```

---

## Example Output

```
──────────────────────────────────────────────
  ORDER REQUEST SUMMARY
──────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
──────────────────────────────────────────────

──────────────────────────────────────────────
  ORDER RESPONSE
──────────────────────────────────────────────
  Order ID   : 3917421
  Status     : FILLED
  Exec Qty   : 0.001
  Avg Price  : 67432.10
  Client OID : abc123xyz
──────────────────────────────────────────────

✅  Order placed successfully.
```

Logs are written to `trading_bot.log` (rotating, up to 5 × 1 MB).

---

## Assumptions

- Uses the **USDT-M** futures testnet (`https://testnet.binancefuture.com`).
- All orders use `reduceOnly=false` by default (opening positions).
- LIMIT orders use `timeInForce=GTC` by default.
- Credentials are loaded from a `.env` file via `python-dotenv`.
- No position management or account balance checks are performed — this is an order placement utility.

---

## Bonus Feature

`STOP_MARKET` order type is supported as the third order type via `--type STOP_MARKET --stop-price <price>`.
