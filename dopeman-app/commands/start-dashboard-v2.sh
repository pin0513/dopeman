#!/bin/bash
#
# DopeMAN - Control Center Dashboard Launcher (Enhanced)
# 啟動前檢查環境，確保完整性
#

set -e

# 自動偵測腳本所在目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMANDS_DIR="$SCRIPT_DIR"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

PORT=8891
WS_PORT=8892
URL="http://localhost:${PORT}/control-center-real.html"
HTTP_LOG="/tmp/dopeman-http.log"
WS_LOG="/tmp/dopeman-websocket.log"

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}🎛️  DopeMAN - Control Center Dashboard${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 步驟 1: 環境檢查
echo -e "${BLUE}📋 步驟 1/4: 環境檢查${NC}"
echo ""

if [ -f "$COMMANDS_DIR/check-environment.py" ]; then
    if python3 "$COMMANDS_DIR/check-environment.py"; then
        echo ""
    else
        echo -e "${RED}❌ 環境檢查失敗${NC}"
        echo "請手動執行: python3 $COMMANDS_DIR/check-environment.py"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  環境檢查腳本不存在，跳過${NC}"
    echo ""
fi

# 步驟 2: 檢查端口
echo -e "${BLUE}📋 步驟 2/4: 檢查端口${NC}"
echo ""

check_port() {
    local port=$1
    local name=$2

    if lsof -i :$port > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  端口 $port ($name) 已被佔用${NC}"
        lsof -i :$port | grep -v COMMAND
        echo ""
        return 1
    else
        echo -e "${GREEN}✅ 端口 $port ($name) 可用${NC}"
        return 0
    fi
}

PORT_OK=true
check_port $PORT "HTTP" || PORT_OK=false
check_port $WS_PORT "WebSocket" || PORT_OK=false

if [ "$PORT_OK" = false ]; then
    echo ""
    echo -e "${YELLOW}💡 提示: 使用以下指令停止舊的伺服器${NC}"
    echo "   ./stop-dashboard.sh"
    exit 1
fi

echo ""

# 步驟 3: 準備資料
echo -e "${BLUE}📋 步驟 3/4: 準備資料${NC}"
echo ""

cd "$COMMANDS_DIR"

# 檢查資料檔案
DATA_FILE="control-center-real-data.json"
if [ ! -f "$DATA_FILE" ]; then
    echo -e "${YELLOW}⚠️  資料檔案不存在，執行掃描...${NC}"
    if [ -f "scan-real-data.py" ]; then
        python3 scan-real-data.py
        echo -e "${GREEN}✅ 資料掃描完成${NC}"
    else
        echo -e "${RED}❌ 找不到 scan-real-data.py${NC}"
        exit 1
    fi
else
    # 檢查檔案年齡
    if [ "$(uname)" = "Darwin" ]; then
        FILE_AGE=$(($(date +%s) - $(stat -f %m "$DATA_FILE")))
    else
        FILE_AGE=$(($(date +%s) - $(stat -c %Y "$DATA_FILE")))
    fi

    HOURS=$((FILE_AGE / 3600))

    if [ $HOURS -gt 6 ]; then
        echo -e "${YELLOW}⚠️  資料檔案已過期 ($HOURS 小時)${NC}"
        echo "   重新掃描中..."
        python3 scan-real-data.py
        echo -e "${GREEN}✅ 資料更新完成${NC}"
    else
        echo -e "${GREEN}✅ 資料檔案新鮮 ($HOURS 小時)${NC}"
    fi
fi

echo ""

# 步驟 4: 啟動伺服器
echo -e "${BLUE}📋 步驟 4/4: 啟動伺服器${NC}"
echo ""

# 啟動 HTTP Server
echo "🌐 啟動 HTTP Server (端口 $PORT)..."
python3 api-server.py > "$HTTP_LOG" 2>&1 &
HTTP_PID=$!
echo "   PID: $HTTP_PID"

sleep 1

# 驗證 HTTP Server
if ! ps -p $HTTP_PID > /dev/null 2>&1; then
    echo -e "${RED}❌ HTTP Server 啟動失敗${NC}"
    cat "$HTTP_LOG"
    exit 1
fi

echo -e "${GREEN}✅ HTTP Server 已啟動${NC}"
echo ""

# 啟動 WebSocket Server
echo "📡 啟動 WebSocket Server (端口 $WS_PORT)..."
python3 websocket-server.py > "$WS_LOG" 2>&1 &
WS_PID=$!
echo "   PID: $WS_PID"

sleep 1

# 驗證 WebSocket Server
if ! ps -p $WS_PID > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  WebSocket Server 啟動失敗（非致命錯誤）${NC}"
else
    echo -e "${GREEN}✅ WebSocket Server 已啟動${NC}"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}🎉 啟動完成！${NC}"
echo ""
echo -e "${CYAN}📍 Dashboard URL:${NC} $URL"
echo -e "${CYAN}📋 HTTP 日誌:${NC} $HTTP_LOG"
echo -e "${CYAN}📋 WebSocket 日誌:${NC} $WS_LOG"
echo ""
echo -e "${YELLOW}💡 提示：${NC}"
echo "   • 使用 ./stop-dashboard.sh 停止伺服器"
echo "   • HTTP Server PID: $HTTP_PID"
echo "   • WebSocket Server PID: $WS_PID"
echo ""

# 開啟瀏覽器
open "$URL"
echo -e "${GREEN}✅ 已開啟瀏覽器${NC}"
echo ""
