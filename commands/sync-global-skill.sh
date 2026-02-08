#!/bin/bash
#
# DopeMAN - Global Skill Sync
# 同步全域 skill 與專案版本
#

set -e

# 顏色輸出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 路徑定義
GLOBAL_SKILL="$HOME/.claude/skills/dopeman/SKILL.md"
PROJECT_SKILL="$HOME/AgentProjects/dopeman/.claude/skills/dopeman/SKILL.md"

echo ""
echo "🔄 DopeMAN - Global Skill Sync"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 檢查檔案是否存在
if [ ! -f "$GLOBAL_SKILL" ]; then
    echo -e "${RED}❌ 全域 SKILL.md 不存在${NC}"
    exit 1
fi

if [ ! -f "$PROJECT_SKILL" ]; then
    echo -e "${RED}❌ 專案 SKILL.md 不存在${NC}"
    exit 1
fi

# 功能選單
echo "選擇同步方向："
echo ""
echo "  1) Pull  - 全域 → 專案 (從全域更新到專案)"
echo "  2) Push  - 專案 → 全域 (從專案推送到全域)"
echo "  3) Diff  - 比較差異"
echo "  4) Status - 檢查狀態"
echo ""
read -p "請選擇 [1-4]: " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}📥 Pull: 全域 → 專案${NC}"
        echo ""

        # 檢查是否有差異
        if diff -q "$GLOBAL_SKILL" "$PROJECT_SKILL" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 兩邊已同步，無需更新${NC}"
        else
            echo "發現差異，正在同步..."
            cp "$GLOBAL_SKILL" "$PROJECT_SKILL"
            echo -e "${GREEN}✅ 已從全域更新到專案${NC}"
        fi
        ;;

    2)
        echo ""
        echo -e "${BLUE}📤 Push: 專案 → 全域${NC}"
        echo ""

        # 檢查是否有差異
        if diff -q "$GLOBAL_SKILL" "$PROJECT_SKILL" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 兩邊已同步，無需更新${NC}"
        else
            echo "發現差異，正在同步..."

            # 備份全域版本
            BACKUP_FILE="${GLOBAL_SKILL}.backup.$(date +%Y%m%d_%H%M%S)"
            cp "$GLOBAL_SKILL" "$BACKUP_FILE"
            echo -e "${YELLOW}📦 已備份全域版本: $BACKUP_FILE${NC}"

            cp "$PROJECT_SKILL" "$GLOBAL_SKILL"
            echo -e "${GREEN}✅ 已從專案推送到全域${NC}"
        fi
        ;;

    3)
        echo ""
        echo -e "${BLUE}📊 差異比較${NC}"
        echo ""

        if diff -q "$GLOBAL_SKILL" "$PROJECT_SKILL" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 兩邊內容相同${NC}"
        else
            echo -e "${YELLOW}⚠️  發現差異：${NC}"
            echo ""
            diff -u "$GLOBAL_SKILL" "$PROJECT_SKILL" || true
        fi
        ;;

    4)
        echo ""
        echo -e "${BLUE}📋 同步狀態${NC}"
        echo ""

        echo "全域 SKILL:"
        echo "  路徑: $GLOBAL_SKILL"
        echo "  大小: $(wc -c < "$GLOBAL_SKILL") bytes"
        echo "  修改: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$GLOBAL_SKILL")"
        echo ""

        echo "專案 SKILL:"
        echo "  路徑: $PROJECT_SKILL"
        echo "  大小: $(wc -c < "$PROJECT_SKILL") bytes"
        echo "  修改: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$PROJECT_SKILL")"
        echo ""

        if diff -q "$GLOBAL_SKILL" "$PROJECT_SKILL" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 狀態: 已同步${NC}"
        else
            echo -e "${YELLOW}⚠️  狀態: 有差異${NC}"
        fi
        ;;

    *)
        echo -e "${RED}❌ 無效選擇${NC}"
        exit 1
        ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
