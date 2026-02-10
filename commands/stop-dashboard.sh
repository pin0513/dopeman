#!/bin/bash
#
# DopeMAN - Control Center Dashboard Stopper
# 停止 HTTP + WebSocket 伺服器
#

set -e

HTTP_PID_FILE="/tmp/dopeman-http.pid"
WS_PID_FILE="/tmp/dopeman-websocket.pid"
HTTP_LOG_FILE="/tmp/dopeman-http.log"
WS_LOG_FILE="/tmp/dopeman-websocket.log"

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}🛑 停止 DopeMAN Dashboard${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 函數：停止單一伺服器
stop_server() {
    local PID_FILE=$1
    local SERVER_NAME=$2

    if [ ! -f "$PID_FILE" ]; then
        echo -e "${YELLOW}⚠️  找不到 ${SERVER_NAME} PID 檔案${NC}"
        return 1
    fi

    local PID=$(cat "$PID_FILE")

    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  ${SERVER_NAME} 已停止 (PID: $PID)${NC}"
        rm -f "$PID_FILE"
        return 0
    fi

    echo "正在停止 ${SERVER_NAME} (PID: $PID)..."
    kill "$PID" 2>/dev/null || true
    sleep 1

    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  使用 SIGKILL 強制停止...${NC}"
        kill -9 "$PID" 2>/dev/null || true
        sleep 1
    fi

    rm -f "$PID_FILE"
    echo -e "${GREEN}✅ ${SERVER_NAME} 已停止${NC}"
    return 0
}

# 停止 HTTP 伺服器
stop_server "$HTTP_PID_FILE" "HTTP Server"

# 停止 WebSocket 伺服器
stop_server "$WS_PID_FILE" "WebSocket Server"

# 備援：停止所有相關的 Python 伺服器
if pgrep -f "python.*http.server.*8891" > /dev/null; then
    echo "清理殘留的 HTTP Server..."
    pkill -f "python.*http.server.*8891"
fi

if pgrep -f "python.*websocket-server.py" > /dev/null; then
    echo "清理殘留的 WebSocket Server..."
    pkill -f "python.*websocket-server.py"
fi

echo ""
echo -e "${GREEN}🎉 所有伺服器已停止${NC}"
echo ""

# 提示日誌位置
if [ -f "$HTTP_LOG_FILE" ]; then
    echo "📋 HTTP 日誌: $HTTP_LOG_FILE"
fi
if [ -f "$WS_LOG_FILE" ]; then
    echo "📋 WebSocket 日誌: $WS_LOG_FILE"
fi
echo ""
