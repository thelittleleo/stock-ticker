import asyncio
import json
import os
from collections import deque
from datetime import datetime, timezone

import httpx
import websockets
from dotenv import load_dotenv

load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
HOST = "localhost"
PORT = 8765
SYMBOLS = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META"]
HISTORY_LEN = 60

# {symbol: deque of price points}
price_history: dict[str, deque] = {sym: deque(maxlen=HISTORY_LEN) for sym in SYMBOLS}
# {symbol: last price} for computing change
last_price: dict[str, float] = {}

# connected browser clients
clients: set = set()


def normalize_trade(trade: dict) -> dict | None:
    """Convert a Finnhub trade entry into a tick dict."""
    sym = trade.get("s")
    price = trade.get("p")
    if not sym or price is None:
        return None

    prev = last_price.get(sym, price)
    change = price - prev
    change_pct = (change / prev * 100) if prev else 0.0

    last_price[sym] = price

    return {
        "ticker": sym,
        "price": price,
        "prev_price": prev,
        "change": round(change, 4),
        "change_pct": round(change_pct, 4),
        "timestamp": trade.get("t", int(datetime.now(timezone.utc).timestamp() * 1000)),
        "volume": trade.get("v", 0),
    }


async def fetch_quotes() -> None:
    """Fetch current quotes from Finnhub REST API and seed price_history."""
    url = "https://finnhub.io/api/v1/quote"
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    async with httpx.AsyncClient(timeout=10) as client:
        tasks = [
            client.get(url, params={"symbol": sym, "token": FINNHUB_API_KEY})
            for sym in SYMBOLS
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    for sym, resp in zip(SYMBOLS, responses):
        if isinstance(resp, Exception):
            print(f"[rest] failed to fetch {sym}: {resp}")
            continue
        if resp.status_code != 200:
            print(f"[rest] {sym} HTTP {resp.status_code}")
            continue
        q = resp.json()
        price = q.get("c")
        prev  = q.get("pc")
        if not price:
            print(f"[rest] {sym} missing price in response: {q}")
            continue
        change     = price - prev if prev else 0.0
        change_pct = (change / prev * 100) if prev else 0.0
        tick = {
            "ticker":     sym,
            "price":      price,
            "prev_price": prev,
            "change":     round(change, 4),
            "change_pct": round(change_pct, 4),
            "timestamp":  now_ms,
            "volume":     0,
        }
        last_price[sym] = price
        price_history[sym].append(tick)
        print(f"[rest] {sym} seeded at {price}")


async def broadcast(payload: dict) -> None:
    if not clients:
        return
    message = json.dumps(payload)
    await asyncio.gather(*[c.send(message) for c in clients], return_exceptions=True)


async def finnhub_listener() -> None:
    """Connect to Finnhub, subscribe to symbols, and forward ticks."""
    url = f"wss://ws.finnhub.io?token={FINNHUB_API_KEY}"
    async for ws in websockets.connect(url):
        try:
            # Subscribe to each symbol
            for sym in SYMBOLS:
                await ws.send(json.dumps({"type": "subscribe", "symbol": sym}))
            print(f"[finnhub] subscribed to {', '.join(SYMBOLS)}")

            async for raw in ws:
                msg = json.loads(raw)
                if msg.get("type") != "trade":
                    continue
                for trade in msg.get("data", []):
                    tick = normalize_trade(trade)
                    if tick is None:
                        continue
                    price_history[tick["ticker"]].append(tick)
                    await broadcast({"type": "tick", "data": tick})

        except websockets.ConnectionClosed as exc:
            print(f"[finnhub] connection closed ({exc}), reconnecting…")
        except Exception as exc:
            print(f"[finnhub] error: {exc}, reconnecting…")


async def client_handler(ws) -> None:
    """Handle a browser WebSocket connection."""
    clients.add(ws)
    remote = ws.remote_address
    print(f"[server] client connected: {remote}  (total: {len(clients)})")

    try:
        # Send snapshot for all symbols — include empty deques so cards always render
        snapshot = {sym: list(price_history[sym]) for sym in SYMBOLS}
        await ws.send(json.dumps({"type": "snapshot", "data": snapshot}))

        # Keep alive — client messages are ignored but we need to hold the loop open
        async for _ in ws:
            pass

    except websockets.ConnectionClosed:
        pass
    finally:
        clients.discard(ws)
        print(f"[server] client disconnected: {remote}  (total: {len(clients)})")


async def main() -> None:
    if not FINNHUB_API_KEY:
        raise RuntimeError("FINNHUB_API_KEY is not set in .env")

    print(f"[server] starting on ws://{HOST}:{PORT}")
    await fetch_quotes()
    async with websockets.serve(client_handler, HOST, PORT):
        await finnhub_listener()  # runs forever (reconnects on drop)


if __name__ == "__main__":
    asyncio.run(main())
