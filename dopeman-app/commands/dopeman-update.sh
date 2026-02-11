#!/bin/bash
#
# DopeMAN Update - 從 GitHub 檢查並更新
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${CYAN}🔄 DopeMAN Update - GitHub 更新檢查${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd "$PROJECT_DIR"

# 檢查是否在 git repo
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ 不是 git repository${NC}"
    echo "   請確認專案目錄: $PROJECT_DIR"
    exit 1
fi

# 1. 檢查遠端狀態
echo -e "${BLUE}📋 步驟 1/4: 檢查遠端狀態${NC}"
echo ""

echo "   Fetching from origin..."
git fetch origin

# 取得當前分支
CURRENT_BRANCH=$(git branch --show-current)
echo "   當前分支: $CURRENT_BRANCH"

# 取得遠端與本地的 commit
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "")

if [ -z "$REMOTE" ]; then
    echo -e "${YELLOW}⚠️  無法取得遠端分支資訊${NC}"
    echo "   可能沒有設定 upstream"
    exit 1
fi

BASE=$(git merge-base @ @{u})

echo ""

# 2. 判斷狀態
echo -e "${BLUE}📋 步驟 2/4: 比對版本${NC}"
echo ""

if [ $LOCAL = $REMOTE ]; then
    echo -e "${GREEN}✅ 已是最新版本${NC}"
    echo "   本地與遠端版本一致"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}🎉 無需更新${NC}"
    echo ""
    exit 0
elif [ $LOCAL = $BASE ]; then
    echo -e "${YELLOW}⚠️  發現新版本${NC}"
    echo ""

    # 顯示變更摘要
    echo "   變更摘要："
    git log --oneline $LOCAL..$REMOTE | head -5

    COMMIT_COUNT=$(git rev-list --count $LOCAL..$REMOTE)
    echo ""
    echo "   共有 $COMMIT_COUNT 個新 commit"
    echo ""
elif [ $REMOTE = $BASE ]; then
    echo -e "${YELLOW}⚠️  本地版本較新${NC}"
    echo "   本地有未推送的 commit"
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}🎉 無需更新（本地較新）${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}❌ 分支已分歧${NC}"
    echo "   本地與遠端都有各自的 commit"
    echo "   建議手動處理 (git pull 或 git rebase)"
    exit 1
fi

# 3. 確認更新
echo -e "${BLUE}📋 步驟 3/4: 確認更新${NC}"
echo ""

read -p "是否要更新到最新版本？ (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  已取消更新${NC}"
    exit 0
fi

echo ""

# 4. 執行更新
echo -e "${BLUE}📋 步驟 4/4: 執行更新${NC}"
echo ""

# 檢查是否有未提交的變更
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}⚠️  有未提交的變更${NC}"
    echo ""
    git status --short
    echo ""

    read -p "是否要 stash 這些變更？ (y/N): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   Stashing changes..."
        git stash push -m "dopeman-update: $(date +%Y%m%d_%H%M%S)"
        echo -e "${GREEN}✅ 變更已 stash${NC}"
        echo ""
        NEED_POP=true
    else
        echo -e "${RED}❌ 取消更新（有未提交變更）${NC}"
        exit 1
    fi
fi

# Pull 最新版本
echo "   Pulling from origin/$CURRENT_BRANCH..."
git pull origin "$CURRENT_BRANCH" --no-rebase

echo ""
echo -e "${GREEN}✅ 更新完成${NC}"
echo ""

# 恢復 stash
if [ "$NEED_POP" = true ]; then
    echo "   恢復 stash 的變更..."
    if git stash pop; then
        echo -e "${GREEN}✅ 變更已恢復${NC}"
    else
        echo -e "${YELLOW}⚠️  恢復變更時發生衝突${NC}"
        echo "   請手動解決衝突，然後執行: git stash drop"
    fi
    echo ""
fi

# 5. 更新 Python 依賴
echo -e "${YELLOW}📋 檢查 Python 依賴...${NC}"
echo ""

if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "   更新 Python 套件..."
    pip3 install -r "$SCRIPT_DIR/requirements.txt" --upgrade --quiet
    echo -e "${GREEN}✅ Python 套件已更新${NC}"
    echo ""
fi

# 6. 同步全域 SKILL.md
echo -e "${YELLOW}📋 同步全域 SKILL.md...${NC}"
echo ""

if [ -f "$SCRIPT_DIR/sync-global-skill.sh" ]; then
    echo "2" | "$SCRIPT_DIR/sync-global-skill.sh" > /tmp/dopeman-sync.log 2>&1
    echo -e "${GREEN}✅ SKILL.md 已同步${NC}"
else
    echo -e "${YELLOW}⚠️  sync-global-skill.sh 不存在，跳過${NC}"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}🎉 更新完成！${NC}"
echo ""
echo -e "${YELLOW}💡 提示：${NC}"
echo "   • 如果 Dashboard 正在執行，請執行 ./dopeman-restart.sh 重啟"
echo "   • 查看更新日誌: git log -5"
echo ""
