# Stock Ticker

A real-time stock price dashboard powered by the [Finnhub](https://finnhub.io) WebSocket and REST APIs.

![Screenshot placeholder](screenshot.png)

## What it does

- Fetches current quotes for 7 symbols (AAPL, MSFT, NVDA, TSLA, AMZN, GOOGL, META) on startup via the Finnhub REST API so cards are populated immediately
- Streams live trade ticks over the Finnhub WebSocket feed
- Serves the data to any connected browser via a local WebSocket server on port 8765
- The frontend renders a scrolling ticker bar, a grid of symbol cards with sparkline charts, and a large detail chart for the selected symbol — all updating in real time with green/red flash animations

## Tech stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.12, asyncio |
| WebSocket server | [websockets](https://websockets.readthedocs.io) |
| HTTP client | [httpx](https://www.python-httpx.org) |
| Config | [python-dotenv](https://pypi.org/project/python-dotenv/) |
| Market data | [Finnhub API](https://finnhub.io/docs/api) |
| Frontend | Vanilla JS, Canvas API — single `index.html`, no build step |

## Local setup

**1. Clone the repo**
```bash
git clone https://github.com/your-username/stock-ticker.git
cd stock-ticker
```

**2. Create your `.env`**
```bash
cp .env.example .env
```
Then open `.env` and replace `your_key_here` with your [Finnhub API key](https://finnhub.io/dashboard).

**3. Create and activate a virtual environment**
```bash
python3 -m virtualenv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

**4. Install dependencies**
```bash
pip install websockets httpx python-dotenv
```

**5. Start the server**
```bash
python server.py
```
You should see REST quotes seeded for all symbols, then `[finnhub] subscribed to …`.

**6. Open the frontend**

Open `index.html` directly in your browser, or serve it locally:
```bash
python -m http.server 8080
# then visit http://localhost:8080
```

## Project structure

```
stock-ticker/
├── server.py        # asyncio WebSocket server + Finnhub client
├── index.html       # single-file vanilla JS frontend
├── .env             # your secrets (not committed)
├── .env.example     # placeholder — safe to commit
└── .gitignore
```
