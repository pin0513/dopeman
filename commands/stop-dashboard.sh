#!/bin/bash
#
# DopeMAN - Control Center Dashboard Stopper
# 停止 Dashboard 伺服器
#

set -e

PID_FILE="/tmp/dopeman-dashboard.pid"
LOG_FILE="/tmp/dopeman-dashboard.log"

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "🛑 停止 DopeMAN Dashboard"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 檢查 PID 檔案是否存在
if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}⚠️  找不到 PID 檔案，伺服器可能未運行${NC}"
    echo ""

    # 嘗試查找並停止所有相關的 Python HTTP 伺服器
    if pgrep -f "python.*http.server.*8891" > /dev/null; then
        echo "發現運行中的伺服器，正在停止..."
        pkill -f "python.*http.server.*8891"
        sleep 1
        echo -e "${GREEN}✅ 已停止伺服器${NC}"
    else
        echo "沒有發現運行中的伺服器"
    fi

    exit 0
fi

# 讀取 PID
PID=$(cat "$PID_FILE")

# 檢查程序是否還在運行
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  伺服器已停止 (PID: $PID)${NC}"
    rm -f "$PID_FILE"
    exit 0
fi

# 停止伺服器
echo "正在停止伺服器 (PID: $PID)..."
kill "$PID" 2>/dev/null || true

# 等待程序停止
sleep 1

# 驗證是否已停止
if ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  使用 SIGKILL 強制停止...${NC}"
    kill -9 "$PID" 2>/dev/null || true
    sleep 1
fi

# 清理 PID 檔案
rm -f "$PID_FILE"

echo -e "${GREEN}✅ 伺服器已停止${NC}"
echo ""

# 提示日誌位置
if [ -f "$LOG_FILE" ]; then
    echo "📋 日誌位置: $LOG_FILE"
    echo ""
fi
