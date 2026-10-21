#!/usr/bin/env bash
# Gemini Multi-Agent Orchestrator 一键启动脚本

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

PORT=8765
SERVER_LOG="$DIR/server.log"
CF_LOG="$DIR/cloudflared.log"
PID_FILE="$DIR/hub.pid"

# 查找具备 google-genai 的 Python 环境
VENV_PY="/Volumes/wisely-data/dev-specs-knowledge-base/.venv/bin/python"
if [ -f "$VENV_PY" ]; then
    PY_BIN="$VENV_PY"
else
    PY_BIN="python3"
fi

# 获取本机局域网 IP
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "127.0.0.1")

echo "=================================================="
echo "🚀 启动 Gemini 跨端多 Agent 协同研发中枢"
echo "=================================================="

# 1. 停止已有进程
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  正在重启端口 $PORT 上的已有进程..."
    kill -9 $(lsof -Pi :$PORT -sTCP:LISTEN -t) 2>/dev/null
    sleep 1
fi
pkill -f "cloudflared tunnel" 2>/dev/null

# 2. 启动本地后台服务
nohup "$PY_BIN" server.py $PORT > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!
echo "✅ 本地中枢服务已启动 [PID: $SERVER_PID]"
echo "   - 本地电脑入口: http://localhost:$PORT"
echo "   - 家中局域网直连 (手机连同WiFi永不掉线): http://${LOCAL_IP}:${PORT}"

# 3. 启动 Cloudflare 隧道 (带 HTTP/2 协议与心跳保活)
echo "🌐 正在建立 Cloudflare 安全外网隧道 (外网/4G/5G随时随地)..."
rm -f "$CF_LOG"
nohup /opt/homebrew/bin/cloudflared tunnel --protocol http2 --url "http://127.0.0.1:$PORT" > "$CF_LOG" 2>&1 &
CF_PID=$!

echo "$SERVER_PID" > "$PID_FILE"
echo "$CF_PID" >> "$PID_FILE"

# 4. 循环等待捕获公网 HTTPS URL
TUNNEL_URL=""
for i in {1..25}; do
    sleep 1
    if [ -f "$CF_LOG" ]; then
        TUNNEL_URL=$(grep -o 'https://[a-zA-Z0-9-]*\.trycloudflare\.com' "$CF_LOG" | grep -v 'api\.trycloudflare\.com' | head -n 1)
        if [ -n "$TUNNEL_URL" ]; then
            break
        fi
    fi
    echo -n "."
done
echo ""

echo "=================================================="
if [ -n "$TUNNEL_URL" ]; then
    echo "🎉 跨端双通道已全部就绪！"
    echo ""
    echo "📱 通道 1: 外网随时随地直连 (4G/5G / 任意网络):"
    echo "👉 $TUNNEL_URL"
    echo ""
    echo "🏠 通道 2: 家中局域网极速直连 (手机连家中WiFi，稳定永不掉线):"
    echo "👉 http://${LOCAL_IP}:${PORT}"
    echo ""
    echo "🖼️ 手机扫码快捷图:"
    echo "   https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=${TUNNEL_URL}"
else
    echo "⚠️ 隧道正在建立中，家中可直接使用局域网: http://${LOCAL_IP}:${PORT}"
fi
echo "=================================================="
