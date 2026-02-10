#!/bin/bash

# 啟動 DopeMAN Control Center Server + WebSocket Server

# 切換到 commands 目錄
cd "$(dirname "$0")"

# PID 檔案位置
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
echo -e "${BLUE}🚀 DopeMAN Control Center 啟動中...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 檢查 Python 是否安裝
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 找不到 Python 3${NC}"
    echo "請先安裝 Python 3"
    exit 1
fi

# 檢查 websockets 模組
if ! python3 -c "import websockets" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  找不到 websockets 模組${NC}"
    echo "正在安裝 websockets..."
    pip3 install websockets
fi

# 停止舊的伺服器（如果存在）
if [ -f "$HTTP_PID_FILE" ]; then
    OLD_PID=$(cat "$HTTP_PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "停止舊的 HTTP 伺服器..."
        kill "$OLD_PID" 2>/dev/null || true
        sleep 1
    fi
    rm -f "$HTTP_PID_FILE"
fi

if [ -f "$WS_PID_FILE" ]; then
    OLD_PID=$(cat "$WS_PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "停止舊的 WebSocket 伺服器..."
        kill "$OLD_PID" 2>/dev/null || true
        sleep 1
    fi
    rm -f "$WS_PID_FILE"
fi

# 給予 Python 腳本執行權限
chmod +x control-center-server.py websocket-server.py

# 智能掃描（6 小時快取）
DATA_FILE="control-center-real-data.json"
CACHE_HOURS=6

if [ -f "$DATA_FILE" ]; then
    # 檢查檔案修改時間
    if [ "$(uname)" = "Darwin" ]; then
        # macOS
        FILE_TIME=$(stat -f %m "$DATA_FILE")
    else
        # Linux
        FILE_TIME=$(stat -c %Y "$DATA_FILE")
    fi

    CURRENT_TIME=$(date +%s)
    TIME_DIFF=$((CURRENT_TIME - FILE_TIME))
    CACHE_SECONDS=$((CACHE_HOURS * 3600))

    if [ $TIME_DIFF -lt $CACHE_SECONDS ]; then
        HOURS_AGO=$((TIME_DIFF / 3600))
        MINUTES_AGO=$(((TIME_DIFF % 3600) / 60))
        echo -e "${GREEN}✅ 使用快取資料${NC} (${HOURS_AGO}h ${MINUTES_AGO}m 前掃描)"
        echo "   下次掃描時間: $((CACHE_HOURS - HOURS_AGO)) 小時後"
    else
        echo -e "${BLUE}🔍 快取已過期，重新掃描...${NC}"
        python3 scan-real-data.py
    fi
else
    echo -e "${BLUE}🔍 初始掃描中...${NC}"
    python3 scan-real-data.py
fi

echo ""

# 啟動 API Server（背景，支援 POST 請求）
echo -e "${BLUE}🌐 啟動 API Server (port 8891)...${NC}"
nohup python3 api-server.py > "$HTTP_LOG_FILE" 2>&1 &
HTTP_PID=$!
echo $HTTP_PID > "$HTTP_PID_FILE"
sleep 1  # 等待伺服器啟動
echo -e "${GREEN}✅ API Server 已啟動 (PID: $HTTP_PID)${NC}"

# 啟動 WebSocket 伺服器（背景）
echo -e "${BLUE}📡 啟動 WebSocket Server (port 8892)...${NC}"
nohup python3 websocket-server.py > "$WS_LOG_FILE" 2>&1 &
WS_PID=$!
echo $WS_PID > "$WS_PID_FILE"
echo -e "${GREEN}✅ WebSocket Server 已啟動 (PID: $WS_PID)${NC}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}🎉 啟動完成！${NC}"
echo ""
echo "📍 Dashboard URL: http://localhost:8891/control-center-real.html"
echo "📊 任務監控 URL: http://localhost:8891/task-monitor.html"
echo "📋 HTTP 日誌: $HTTP_LOG_FILE"
echo "📋 WebSocket 日誌: $WS_LOG_FILE"
echo ""
echo "💡 使用 ./stop-dashboard.sh 停止伺服器"
echo ""

# 自動開啟瀏覽器
sleep 2
if command -v open &> /dev/null; then
    open "http://localhost:8891/control-center-real.html"
    echo -e "${GREEN}✅ 已開啟瀏覽器${NC}"
elif command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:8891/control-center-real.html"
    echo -e "${GREEN}✅ 已開啟瀏覽器${NC}"
else
    echo -e "${YELLOW}⚠️  請手動開啟瀏覽器${NC}"
fi

echo ""
