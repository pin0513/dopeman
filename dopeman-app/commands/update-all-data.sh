#!/bin/bash
# DopeMAN - 更新所有資料（Skills + 個人資訊匯流）

cd "$(dirname "$0")"

echo "============================================================"
echo "🚀 DopeMAN 資料更新"
echo "============================================================"
echo ""

# 1. 更新 Skills/Agents/Projects 資料
echo "📦 1/2 更新 Skills/Agents/Projects 資料..."
python3 scan-real-data.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ 成功"
else
    echo "   ❌ 失敗"
fi
echo ""

# 2. 更新個人資訊匯流資料（PTT + 台股 v2 with yfinance）
echo "🌐 2/2 更新個人資訊匯流資料（PTT + 台股 v2）..."
python3 fetch-ptt-stocks-v2.py > /tmp/dopeman-fetch.log 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ 成功"
    echo ""
    echo "📊 爬蟲結果："
    grep "📊 統計：" /tmp/dopeman-fetch.log -A 3
else
    echo "   ❌ 失敗"
    echo "   查看日誌: /tmp/dopeman-fetch.log"
fi

echo ""
echo "============================================================"
echo "✅ 更新完成！請重新載入網頁查看最新資料"
echo "============================================================"
echo "📍 Dashboard URL: http://localhost:8891/control-center-v2.html"
echo ""
