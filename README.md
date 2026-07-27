# Real-Time Financial Analytics & Technical Dashboard

A production-ready Python web application that streams live BTC/USDT market data from Binance, calculates technical indicators, and displays them in a polished dark-mode dashboard built with FastAPI and Chart.js.

## Overview

This project delivers a complete full-stack example of a real-time financial analytics experience with:

- Live market updates over WebSockets
- A responsive dashboard UI with animated charts
- Technical indicators including SMA (14) and RSI (14)
- A lightweight Python backend with FastAPI
- Clean deployment-ready structure for local or cloud hosting

## Architecture

The application is organized into three layers:

1. Backend service
   - Built with FastAPI
   - Connects to a Binance WebSocket stream for 1-minute candlestick updates
   - Computes SMA 14 and RSI 14 from the rolling price history
   - Broadcasts the latest market snapshot to all connected clients

2. WebSocket communication
   - The frontend opens a WebSocket connection to the FastAPI server
   - The server pushes periodic updates to the browser without reloading the page

3. Frontend dashboard
   - A static HTML page served from the FastAPI app
   - Uses Chart.js to render a live animated line chart
   - Displays the latest price, change percentage, SMA, and RSI values

## Features

- Real-time BTC/USDT price stream
- Live percentage change tracking
- Moving average indicator (SMA 14)
- Relative strength index (RSI 14)
- Dark-mode UI with responsive cards and chart layout
- Health endpoint for monitoring
- WebSocket-based push updates for low-latency rendering

## Project Structure

- main.py — FastAPI app, Binance WebSocket client, indicator calculations, and WebSocket broadcast logic
- static/index.html — Dashboard HTML, styling, Chart.js integration, and browser-side WebSocket handling
- requirements.txt — Python dependencies
- .gitignore — Python and editor ignore rules

## Requirements

- Python 3.10+
- pip

## Setup

1. Clone or open the project directory.
2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the application:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

5. Open the dashboard in your browser:

```text
http://127.0.0.1:8000/
```

## API Endpoints

- GET / — Serves the dashboard UI
- GET /health — Health check endpoint returning service status
- WebSocket /ws/market — Streams market updates to the frontend

## Deployment Notes

This app is ready to be deployed on platforms such as:

- Render
- Railway
- Fly.io
- Azure App Service
- Any Linux server with Python and a reverse proxy

For production deployments, consider adding:

- HTTPS termination
- Environment-based configuration
- Logging and monitoring
- Authentication or rate limiting if exposing public endpoints

## Notes

The dashboard uses Binance’s public WebSocket feed for market data. Network availability and exchange connectivity can affect live updates, but the UI remains functional even if the stream briefly disconnects.
