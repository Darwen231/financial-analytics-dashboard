import asyncio
import json
from collections import deque
from datetime import datetime, timezone
from typing import Deque, Dict, Set

import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = "/workspaces/financial-analytics-dashboard"

app = FastAPI(title="Real-Time Financial Analytics Dashboard", version="1.0.0")
app.mount("/static", StaticFiles(directory=f"{BASE_DIR}/static"), name="static")

BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

clients: Set[WebSocket] = set()
price_history: Deque[float] = deque(maxlen=120)
latest_snapshot: Dict[str, object] = {
    "symbol": "BTC/USDT",
    "price": 0.0,
    "changePercent": 0.0,
    "sma14": 0.0,
    "rsi14": 50.0,
    "timestamp": datetime.now(timezone.utc).timestamp() * 1000,
}


class MarketPayload(BaseModel):
    symbol: str
    price: float
    changePercent: float
    sma14: float | None
    rsi14: float | None
    timestamp: int


def calculate_sma(prices: Deque[float], period: int) -> float | None:
    if len(prices) < period:
        return None
    return sum(list(prices)[-period:]) / period


def calculate_rsi(prices: Deque[float], period: int) -> float | None:
    if len(prices) < period + 1:
        return None

    series = list(prices)[-(period + 1) :]
    changes = [series[i] - series[i - 1] for i in range(1, len(series))]
    gains = [max(change, 0.0) for change in changes]
    losses = [abs(min(change, 0.0)) for change in changes]

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


async def broadcast_snapshot(snapshot: Dict[str, object]) -> None:
    if not clients:
        return

    stale_clients: Set[WebSocket] = set()
    for client in list(clients):
        try:
            await client.send_json({"type": "update", "data": snapshot})
        except Exception:
            stale_clients.add(client)

    for stale_client in stale_clients:
        clients.discard(stale_client)


async def stream_binance_updates() -> None:
    while True:
        try:
            async with websockets.connect(BINANCE_WS_URL, ping_interval=None) as websocket:
                async for raw_message in websocket:
                    payload = json.loads(raw_message)
                    if payload.get("e") != "kline":
                        continue

                    candle = payload.get("k", {})
                    if not candle.get("x"):
                        continue

                    close_price = float(candle.get("c", 0.0))
                    price_history.append(close_price)
                    timestamp = int(candle.get("T", datetime.now(timezone.utc).timestamp() * 1000))

                    previous_close = list(price_history)[-2] if len(price_history) >= 2 else close_price
                    change_percent = ((close_price / previous_close) - 1.0) * 100.0 if previous_close else 0.0

                    snapshot = {
                        "symbol": "BTC/USDT",
                        "price": close_price,
                        "changePercent": round(change_percent, 2),
                        "sma14": round(calculate_sma(price_history, 14), 2) if calculate_sma(price_history, 14) is not None else None,
                        "rsi14": round(calculate_rsi(price_history, 14), 2) if calculate_rsi(price_history, 14) is not None else None,
                        "timestamp": timestamp,
                    }
                    latest_snapshot.update(snapshot)
                    await broadcast_snapshot(snapshot)
        except Exception as exc:
            print(f"Binance stream error: {exc}")
        await asyncio.sleep(3)


@app.on_event("startup")
async def startup_event() -> None:
    asyncio.create_task(stream_binance_updates())


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def get_dashboard() -> FileResponse:
    return FileResponse(f"{BASE_DIR}/static/index.html")


@app.websocket("/ws/market")
async def market_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    clients.add(websocket)
    await websocket.send_json({"type": "snapshot", "data": latest_snapshot})

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        clients.discard(websocket)
