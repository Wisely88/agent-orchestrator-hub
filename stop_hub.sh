#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PID_FILE="$DIR/hub.pid"

if [ -f "$PID_FILE" ]; then
    echo "🛑 正在停止 Gemini 跨端协同服务与 Cloudflare 隧道..."
    while IFS= read -r pid; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
            echo "   已终止进程: $pid"
        fi
    done < "$PID_FILE"
    rm -f "$PID_FILE"
    echo "✅ 服务已完全停止。"
else
    echo "未找到运行中的 PID 文件，尝试按端口停止..."
    kill -9 $(lsof -Pi :8765 -sTCP:LISTEN -t) 2>/dev/null
    pkill -f "cloudflared tunnel" 2>/dev/null
    echo "✅ 清理完成。"
fi
