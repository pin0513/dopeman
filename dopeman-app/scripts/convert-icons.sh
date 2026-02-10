#!/bin/bash

# DopeMAN - 圖示轉換腳本
# 將 icon-1024.png 轉換為各平台所需格式

set -e

cd "$(dirname "$0")/../assets"

echo "🎨 DopeMAN 圖示轉換工具"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 檢查來源檔案
if [ ! -f "icon-1024.png" ]; then
    echo "❌ 找不到 icon-1024.png"
    exit 1
fi

echo "✅ 找到來源檔案: icon-1024.png"

# ============================================================
# macOS .icns 轉換
# ============================================================

echo ""
echo "📱 轉換 macOS 圖示 (.icns)..."

if command -v sips &> /dev/null && command -v iconutil &> /dev/null; then
    # 建立 iconset 目錄
    rm -rf icon.iconset
    mkdir -p icon.iconset

    echo "   生成各種尺寸..."

    # 生成所有需要的尺寸
    sips -z 16 16     icon-1024.png --out icon.iconset/icon_16x16.png > /dev/null 2>&1
    sips -z 32 32     icon-1024.png --out icon.iconset/icon_16x16@2x.png > /dev/null 2>&1
    sips -z 32 32     icon-1024.png --out icon.iconset/icon_32x32.png > /dev/null 2>&1
    sips -z 64 64     icon-1024.png --out icon.iconset/icon_32x32@2x.png > /dev/null 2>&1
    sips -z 128 128   icon-1024.png --out icon.iconset/icon_128x128.png > /dev/null 2>&1
    sips -z 256 256   icon-1024.png --out icon.iconset/icon_128x128@2x.png > /dev/null 2>&1
    sips -z 256 256   icon-1024.png --out icon.iconset/icon_256x256.png > /dev/null 2>&1
    sips -z 512 512   icon-1024.png --out icon.iconset/icon_256x256@2x.png > /dev/null 2>&1
    sips -z 512 512   icon-1024.png --out icon.iconset/icon_512x512.png > /dev/null 2>&1
    sips -z 1024 1024 icon-1024.png --out icon.iconset/icon_512x512@2x.png > /dev/null 2>&1

    # 轉換為 .icns
    iconutil -c icns icon.iconset

    # 清理
    rm -rf icon.iconset

    echo "   ✅ icon.icns 已生成"
else
    echo "   ⚠️  未找到 sips/iconutil，跳過 macOS 圖示轉換"
    echo "   （此工具僅在 macOS 上可用）"
fi

# ============================================================
# Windows .ico 轉換
# ============================================================

echo ""
echo "🪟 轉換 Windows 圖示 (.ico)..."

if command -v convert &> /dev/null; then
    # 使用 ImageMagick
    convert icon-1024.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico
    echo "   ✅ icon.ico 已生成"
elif command -v magick &> /dev/null; then
    # Windows 上的 ImageMagick
    magick icon-1024.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico
    echo "   ✅ icon.ico 已生成"
else
    echo "   ⚠️  未找到 ImageMagick，跳過 Windows 圖示轉換"
    echo "   請安裝: brew install imagemagick"
    echo "   或使用線上工具: https://convertico.com/"
fi

# ============================================================
# PNG 備份（通用）
# ============================================================

echo ""
echo "🖼️  建立通用 PNG 圖示..."

if command -v sips &> /dev/null; then
    sips -z 512 512 icon-1024.png --out icon-512.png > /dev/null 2>&1
    sips -z 256 256 icon-1024.png --out icon-256.png > /dev/null 2>&1
    echo "   ✅ icon-512.png, icon-256.png 已生成"
elif command -v convert &> /dev/null; then
    convert icon-1024.png -resize 512x512 icon-512.png
    convert icon-1024.png -resize 256x256 icon-256.png
    echo "   ✅ icon-512.png, icon-256.png 已生成"
else
    echo "   ⚠️  未找到圖片處理工具"
fi

# ============================================================
# 托盤圖示
# ============================================================

echo ""
echo "📌 處理托盤圖示..."

if [ -f "tray-icon.png" ] || [ -f "tray-icon-template.png" ]; then
    # 托盤圖示應該是較小尺寸
    if command -v sips &> /dev/null; then
        if [ -f "tray-icon.png" ]; then
            sips -z 32 32 tray-icon.png --out tray-icon-32.png > /dev/null 2>&1
            cp tray-icon.png tray-icon-original.png
        fi
        if [ -f "tray-icon-template.png" ]; then
            sips -z 32 32 tray-icon-template.png --out tray-icon-32.png > /dev/null 2>&1
        fi
        echo "   ✅ tray-icon-32.png 已生成"
    fi
else
    echo "   ⚠️  找不到托盤圖示來源檔案"
fi

# ============================================================
# 完成
# ============================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ 圖示轉換完成！"
echo ""
echo "已生成檔案："
ls -lh *.png *.icns *.ico 2>/dev/null | awk '{print "  - " $9 " (" $5 ")"}'

echo ""
echo "💡 提示："
echo "  - macOS 打包需要: icon.icns"
echo "  - Windows 打包需要: icon.ico"
echo "  - Linux 打包需要: icon.png"
echo ""
