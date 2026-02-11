#!/bin/bash
#
# DopeMAN Fix - 自動修復常見問題
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
echo -e "${CYAN}🔧 DopeMAN Fix - 自動修復${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd "$SCRIPT_DIR"

# 1. 執行環境檢查（自動修復模式）
echo -e "${YELLOW}📋 執行環境檢查與修復...${NC}"
echo ""

if [ -f "check-environment.py" ]; then
    python3 check-environment.py
else
    echo -e "${RED}❌ 找不到 check-environment.py${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 2. 檢查並修復 SKILL.md
echo -e "${YELLOW}📋 檢查 SKILL.md...${NC}"

HOME_DIR="$HOME"
GLOBAL_SKILL_DIR="$HOME_DIR/.claude/skills/dopeman"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROJECT_SKILL_MD="$PROJECT_DIR/.claude/skills/dopeman/SKILL.md"

if [ ! -f "$GLOBAL_SKILL_DIR/SKILL.md" ]; then
    echo -e "${YELLOW}⚠️  全域 SKILL.md 不存在${NC}"

    if [ -f "$PROJECT_SKILL_MD" ]; then
        echo "   建立 symlink..."
        cd "$GLOBAL_SKILL_DIR"
        ln -sf ".claude/skills/dopeman/SKILL.md" SKILL.md
        echo -e "${GREEN}✅ SKILL.md symlink 已創建${NC}"
    else
        echo -e "${RED}❌ 專案 SKILL.md 也不存在${NC}"
    fi
else
    echo -e "${GREEN}✅ SKILL.md 存在${NC}"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 3. 清理損壞的 symlinks
echo -e "${YELLOW}📋 清理損壞的 symlinks...${NC}"

SKILLS_DIR="$HOME_DIR/.claude/skills"
BROKEN_COUNT=0

if [ -d "$SKILLS_DIR" ]; then
    for link in "$SKILLS_DIR"/*; do
        if [ -L "$link" ] && [ ! -e "$link" ]; then
            echo "   刪除損壞的 symlink: $(basename "$link")"
            rm "$link"
            ((BROKEN_COUNT++))
        fi
    done
fi

if [ $BROKEN_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ 沒有損壞的 symlinks${NC}"
else
    echo -e "${GREEN}✅ 已清理 $BROKEN_COUNT 個損壞的 symlinks${NC}"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 4. 同步 SKILL.md
echo -e "${YELLOW}📋 同步 SKILL.md...${NC}"

if [ -f "../commands/sync-global-skill.sh" ]; then
    cd "$PROJECT_DIR/commands"
    echo "4" | ./sync-global-skill.sh > /tmp/dopeman-sync.log 2>&1
    echo -e "${GREEN}✅ SKILL.md 同步檢查完成${NC}"
else
    echo -e "${YELLOW}⚠️  sync-global-skill.sh 不存在，跳過${NC}"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}🎉 修復完成！${NC}"
echo ""
