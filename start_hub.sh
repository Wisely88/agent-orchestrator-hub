#!/usr/bin/env bash
set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

PORT="${HUB_PORT:-8765}"
HOST="${HUB_HOST:-0.0.0.0}"
SERVER_LOG="$DIR/server.log"
PID_FILE="$DIR/hub.pid"

if lsof -Pi :"$PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
  echo "端口 $PORT 已被占用；为避免误杀其他进程，停止启动。"
  exit 1
fi

if [ -z "${PYTHON_BIN:-}" ]; then
  if [ -x "/Volumes/wisely-data/dev-specs-knowledge-base/.venv/bin/python" ]; then
    PY_BIN="/Volumes/wisely-data/dev-specs-knowledge-base/.venv/bin/python"
  else
    PY_BIN="python3"
  fi
else
  PY_BIN="$PYTHON_BIN"
fi

nohup "$PY_BIN" server.py "$PORT" "$HOST" > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!
echo "$SERVER_PID" > "$PID_FILE"

sleep 1
if ! kill -0 "$SERVER_PID" 2>/dev/null; then
  echo "服务启动失败，日志：$SERVER_LOG"
  cat "$SERVER_LOG"
  rm -f "$PID_FILE"
  exit 1
fi

echo "服务已启动： http://127.0.0.1:$PORT"
echo "安全策略：仅本机监听；不启动 Cloudflare 隧道。"
echo "日志：$SERVER_LOG"
echo "停止服务：./stop_hub.sh"
