#!/usr/bin/env bash
set -euo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PID_FILE="$DIR/hub.pid"

if [ -f "$PID_FILE" ]; then
  while IFS= read -r pid; do
    if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid"
      echo "已请求停止进程：$pid"
    fi
  done < "$PID_FILE"
  rm -f "$PID_FILE"
else
  echo "未找到 PID 文件；未尝试按端口强制杀进程。"
fi
