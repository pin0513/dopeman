#!/bin/bash
#
# DopeMAN Restart - 重啟 Dashboard
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}🔄 DopeMAN Restart - 重啟 Dashboard${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd "$SCRIPT_DIR"

# 1. 停止現有伺服器
echo -e "${YELLOW}📋 停止現有伺服器...${NC}"
echo ""

if [ -f "./stop-dashboard.sh" ]; then
    ./stop-dashboard.sh
    echo ""
else
    echo -e "${YELLOW}⚠️  stop-dashboard.sh 不存在，嘗試手動停止${NC}"

    # 手動停止
    HTTP_PID=$(lsof -t -i:8891 2>/dev/null || true)
    WS_PID=$(lsof -t -i:8892 2>/dev/null || true)

    if [ -n "$HTTP_PID" ]; then
        echo "   停止 HTTP Server (PID: $HTTP_PID)..."
        kill "$HTTP_PID" 2>/dev/null || true
    fi

    if [ -n "$WS_PID" ]; then
        echo "   停止 WebSocket Server (PID: $WS_PID)..."
        kill "$WS_PID" 2>/dev/null || true
    fi

    sleep 2
    echo -e "${GREEN}✅ 伺服器已停止${NC}"
    echo ""
fi

# 2. 啟動新伺服器
echo -e "${YELLOW}📋 啟動新伺服器...${NC}"
echo ""

if [ -f "./start-dashboard-v2.sh" ]; then
    ./start-dashboard-v2.sh
else
    echo -e "${RED}❌ start-dashboard-v2.sh 不存在${NC}"
    echo "   請檢查檔案是否存在"
    exit 1
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}🎉 重啟完成！${NC}"
echo ""
