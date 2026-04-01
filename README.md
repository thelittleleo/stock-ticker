# Stock Ticker

A real-time stock and crypto dashboard powered by the [Finnhub](https://finnhub.io) API.
Prices stream live via WebSocket, cards flash green/red on every tick, and your portfolio
and price alerts are saved locally in the browser.

![Screenshot](assets/screenshot.png)

---

## Features

- **Live price stream** — trades pushed over WebSocket, cards flash green/red on every tick
- **Sparkline charts** — 60-point Canvas sparkline per card, full detail chart on click
- **Stocks** — AAPL, MSFT, NVDA, TSLA, AMZN, GOOGL, META seeded from REST on startup
- **Crypto** — BTC/USDT, ETH/USDT, SOL/USDT, XRP/USDT, BNB/USDT via Binance feed
- **Scrolling ticker bar** — all symbols scroll across the top, pauses on hover
- **Portfolio tracker** — enter quantity + buy price per symbol; live P&L table with totals
- **Price alerts** — set a target price on any symbol; browser notification fires once when crossed
- **Auto-reconnect** — client reconnects every 3 seconds if the server drops
- **Zero frontend dependencies** — single `index.html`, vanilla JS + Canvas API, no build step

---

## Tech stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.12, `asyncio` |
| WebSocket server | [`websockets`](https://websockets.readthedocs.io) |
| HTTP client | [`httpx`](https://www.python-httpx.org) (concurrent REST seed fetches) |
| Config | [`python-dotenv`](https://pypi.org/project/python-dotenv/) |
| Market data | [Finnhub API](https://finnhub.io/docs/api) — REST quotes + WebSocket trades |
| Crypto feed | Binance symbols via Finnhub WebSocket (`BINANCE:BTCUSDT`, etc.) |
| Frontend | Vanilla JS, Canvas API — single `index.html` |
| Hosting | [Railway](https://railway.app) (server) + [GitHub Pages](https://pages.github.com) (frontend) |

---

## Local setup

**1. Clone**
```bash
git clone https://github.com/thelittleleo/stock-ticker.git
cd stock-ticker
```

**2. Create `.env`**
```bash
cp .env.example .env
# then edit .env and set your Finnhub API key:
# FINNHUB_API_KEY=your_key_here
```
Get a free key at [finnhub.io/dashboard](https://finnhub.io/dashboard).

**3. Create virtual environment and install dependencies**
```bash
python3 -m virtualenv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**4. Start the server**
```bash
python server.py
```
On startup the server fetches current quotes for all 7 stock symbols via REST,
then opens the WebSocket connection to Finnhub and starts streaming trades.

```
[rest] AAPL seeded at 213.49
[rest] MSFT seeded at 415.20
...
[finnhub] subscribed to 12 symbols (7 stocks, 5 crypto)
[server] starting on ws://0.0.0.0:8765
```

**5. Open the frontend**

Open `index.html` directly in your browser — it auto-detects `file://` protocol
and connects to `ws://localhost:8765`. Or serve it:

```bash
python -m http.server 8080
# visit http://localhost:8080
```

---

## Deployment

The server runs on [Railway](https://railway.app) and the frontend is hosted on
[GitHub Pages](https://pages.github.com).

- Railway injects `PORT` automatically; the server reads `int(os.environ.get("PORT", 8765))`
- Set `FINNHUB_API_KEY` in Railway's Variables tab
- The frontend uses `wss://` when not on localhost, pointing at `RAILWAY_DOMAIN` in `index.html`

---

## Project structure

```
stock-ticker/
├── server.py        # asyncio WebSocket server + Finnhub REST/WS client
├── index.html       # single-file vanilla JS frontend
├── requirements.txt # websockets, httpx, python-dotenv
├── Procfile         # Railway: web: python server.py
├── assets/
│   └── screenshot.png   # ← drop your screenshot here
├── .env             # your secrets (not committed)
└── .env.example     # FINNHUB_API_KEY=your_key_here
```
