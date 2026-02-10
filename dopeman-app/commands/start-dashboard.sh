#!/bin/bash
#
# DopeMAN - Control Center Dashboard Launcher
# 啟動後端伺服器並開啟 Dashboard
#

set -e

# 配置
COMMANDS_DIR="/Users/paul_huang/AgentProjects/dopeman/commands"
PORT=8891
URL="http://localhost:${PORT}/control-center-real.html"
PID_FILE="/tmp/dopeman-dashboard.pid"
LOG_FILE="/tmp/dopeman-dashboard.log"

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "🎛️  DopeMAN - Control Center Dashboard"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 檢查是否已有伺服器運行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  伺服器已在運行中 (PID: $OLD_PID)${NC}"
        echo ""
        echo "📍 Dashboard URL: $URL"
        echo ""

        # 直接開啟瀏覽器
        open "$URL"
        echo -e "${GREEN}✅ 已開啟瀏覽器${NC}"
        exit 0
    else
        # PID 檔案存在但程序已停止，清理 PID 檔案
        rm -f "$PID_FILE"
    fi
fi

# 檢查端口是否被佔用
if lsof -i :$PORT > /dev/null 2>&1; then
    echo -e "${RED}❌ 端口 $PORT 已被佔用${NC}"
    echo ""
    echo "正在使用端口 $PORT 的程序："
    lsof -i :$PORT
    echo ""
    echo "請先停止該程序，或修改 PORT 配置"
    exit 1
fi

# 切換到 commands 目錄
cd "$COMMANDS_DIR"

# 檢查必要檔案是否存在
if [ ! -f "control-center-real.html" ]; then
    echo -e "${RED}❌ 找不到 control-center-real.html${NC}"
    exit 1
fi

if [ ! -f "control-center-real-data.json" ]; then
    echo -e "${YELLOW}⚠️  找不到 control-center-real-data.json，執行掃描...${NC}"
    echo ""

    if [ -f "scan-real-data.py" ]; then
        python3 scan-real-data.py
        echo ""
    else
        echo -e "${RED}❌ 找不到 scan-real-data.py${NC}"
        exit 1
    fi
fi

# 啟動 HTTP 伺服器
echo "🚀 啟動 HTTP 伺服器..."
echo "   目錄: $COMMANDS_DIR"
echo "   端口: $PORT"
echo ""

nohup python3 -m http.server $PORT > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# 儲存 PID
echo "$SERVER_PID" > "$PID_FILE"

# 等待伺服器啟動
sleep 2

# 驗證伺服器是否成功啟動
if ! ps -p "$SERVER_PID" > /dev/null 2>&1; then
    echo -e "${RED}❌ 伺服器啟動失敗${NC}"
    echo ""
    echo "查看日誌："
    cat "$LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi

# 驗證 HTTP 可訪問
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL")
if [ "$HTTP_STATUS" != "200" ]; then
    echo -e "${RED}❌ Dashboard 無法訪問 (HTTP $HTTP_STATUS)${NC}"
    kill "$SERVER_PID" 2>/dev/null || true
    rm -f "$PID_FILE"
    exit 1
fi

echo -e "${GREEN}✅ 伺服器已啟動 (PID: $SERVER_PID)${NC}"
echo ""
echo "📍 Dashboard URL: $URL"
echo "📋 日誌位置: $LOG_FILE"
echo "🔧 PID 檔案: $PID_FILE"
echo ""

# 開啟瀏覽器
open "$URL"
echo -e "${GREEN}✅ 已開啟瀏覽器${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 提示："
echo "   - 伺服器將持續運行在背景"
echo "   - 關閉瀏覽器不會停止伺服器"
echo "   - 使用 /dopeman stop-dashboard 停止伺服器"
echo "   - 或手動停止: kill $SERVER_PID"
echo ""
