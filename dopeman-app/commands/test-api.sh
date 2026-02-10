#!/bin/bash

echo "🧪 測試 Control Center Server API"
echo "================================"

# 1. 檢查伺服器是否運行
if ! lsof -i :8891 > /dev/null 2>&1; then
    echo "❌ 伺服器未運行，正在啟動..."
    python3 control-center-server.py &
    SERVER_PID=$!
    echo "等待伺服器啟動..."
    sleep 5
else
    echo "✅ 伺服器已在運行"
fi

# 2. 測試 GET 請求
echo ""
echo "📡 測試 GET /control-center-real.html..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8891/control-center-real.html

# 3. 測試 POST /api/rescan
echo ""
echo "📡 測試 POST /api/rescan..."
echo "（這會執行 scan-real-data.py，可能需要 10-30 秒）"

RESPONSE=$(curl -s -X POST http://localhost:8891/api/rescan)

# 檢查回應
if echo "$RESPONSE" | grep -q '"success": true'; then
    echo "✅ API 測試成功！"
    echo "$RESPONSE" | python3 -m json.tool | head -10
else
    echo "❌ API 測試失敗"
    echo "$RESPONSE"
fi

echo ""
echo "================================"
echo "測試完成！"
