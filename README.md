# WhoHats backend

FastAPI service for WhoHats: random partner search over WebSocket and WebRTC signaling.

## Stack

- Python 3.13, FastAPI, uv
- WebSocket events for chat, WebRTC signaling messages for calls

## Run

```
uv sync
uv run main.py
```

Copy `.env.example` to `.env` and adjust settings if needed.

## Layout

```
app/core     # settings and websocket registry
app/ws       # connection manager and chat message handlers
app/routers  # websocket endpoint
app/schemas  # message models
static       # styles and logo
```
