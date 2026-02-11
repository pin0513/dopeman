#!/bin/bash
#
# DopeMAN Dashboard 重構版本測試腳本
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}🧪 DopeMAN Dashboard 重構版本測試${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 測試 1: 檢查檔案存在
echo -e "${YELLOW}📋 測試 1/5: 檢查檔案完整性${NC}"
echo ""

FILES=(
    "control-center-v2.html"
    "css/dashboard-variables.css"
    "css/dashboard-layout.css"
    "css/dashboard-legacy.css"
    "js/dashboard-config.js"
    "js/dashboard-state.js"
    "js/dashboard-api.js"
    "js/dashboard-legacy.js"
)

MISSING_FILES=0

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file (缺失)${NC}"
        ((MISSING_FILES++))
    fi
done

if [ $MISSING_FILES -eq 0 ]; then
    echo -e "\n${GREEN}✅ 所有檔案完整${NC}"
else
    echo -e "\n${RED}❌ 缺少 $MISSING_FILES 個檔案${NC}"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 測試 2: 檢查 CSS 變數
echo -e "${YELLOW}📋 測試 2/5: 檢查 CSS 變數定義${NC}"
echo ""

CSS_VARS_COUNT=$(grep -c "^  --" css/dashboard-variables.css || true)

echo "   CSS 變數數量: $CSS_VARS_COUNT"

if [ $CSS_VARS_COUNT -gt 50 ]; then
    echo -e "${GREEN}✅ CSS 變數系統完整（> 50 個變數）${NC}"
else
    echo -e "${YELLOW}⚠️  CSS 變數較少（建議 > 50 個）${NC}"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 測試 3: 檢查 JavaScript 模組
echo -e "${YELLOW}📋 測試 3/5: 檢查 JavaScript 模組${NC}"
echo ""

MODULES=(
    "DashboardConfig"
    "DashboardState"
    "DashboardAPI"
)

for module in "${MODULES[@]}"; do
    if grep -q "$module" js/dashboard-*.js; then
        echo -e "${GREEN}✅ $module 模組定義${NC}"
    else
        echo -e "${RED}❌ $module 模組缺失${NC}"
    fi
done

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 測試 4: 檔案大小對比
echo -e "${YELLOW}📋 測試 4/5: 檔案大小分析${NC}"
echo ""

ORIGINAL_SIZE=$(stat -f%z "control-center-real.html" 2>/dev/null || stat -c%s "control-center-real.html" 2>/dev/null || echo "0")
REFACTORED_SIZE=$(stat -f%z "control-center-v2.html" 2>/dev/null || stat -c%s "control-center-v2.html" 2>/dev/null || echo "0")

ORIGINAL_KB=$((ORIGINAL_SIZE / 1024))
REFACTORED_KB=$((REFACTORED_SIZE / 1024))
REDUCTION=$((100 - (REFACTORED_SIZE * 100 / ORIGINAL_SIZE)))

echo "   原始版本: ${ORIGINAL_KB} KB"
echo "   重構版本: ${REFACTORED_KB} KB"
echo -e "   ${GREEN}減少: ${REDUCTION}%${NC}"

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 測試 5: HTML 語法檢查
echo -e "${YELLOW}📋 測試 5/5: HTML 語法檢查${NC}"
echo ""

# 檢查是否有基本的 HTML 結構
if grep -q "<!DOCTYPE html>" control-center-v2.html && \
   grep -q "<html lang=\"zh-TW\">" control-center-v2.html && \
   grep -q "</html>" control-center-v2.html; then
    echo -e "${GREEN}✅ HTML 語法結構完整${NC}"
else
    echo -e "${RED}❌ HTML 語法異常${NC}"
fi

# 檢查是否有引入模組化檔案
if grep -q "dashboard-variables.css" control-center-v2.html && \
   grep -q "dashboard-config.js" control-center-v2.html; then
    echo -e "${GREEN}✅ 模組化檔案正確引入${NC}"
else
    echo -e "${YELLOW}⚠️  模組化檔案引入異常${NC}"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}🎉 測試完成！${NC}"
echo ""
echo -e "${YELLOW}📍 下一步：${NC}"
echo "   1. 在瀏覽器中開啟: open control-center-v2.html"
echo "   2. 檢查瀏覽器 Console 是否有錯誤"
echo "   3. 測試所有功能是否正常"
echo "   4. 確認無誤後可切換到重構版本"
echo ""
