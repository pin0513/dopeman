#!/bin/bash

# 啟動 DopeMAN Control Center Server

# 切換到 commands 目錄
cd "$(dirname "$0")"

# 檢查 Python 是否安裝
if ! command -v python3 &> /dev/null; then
    echo "❌ 找不到 Python 3"
    echo "請先安裝 Python 3"
    exit 1
fi

# 給予 Python 腳本執行權限
chmod +x control-center-server.py

# 先執行一次掃描（確保資料最新）
echo "🔍 初始掃描中..."
python3 scan-real-data.py

# 啟動伺服器
echo ""
echo "🚀 啟動 Control Center Server..."
python3 control-center-server.py
