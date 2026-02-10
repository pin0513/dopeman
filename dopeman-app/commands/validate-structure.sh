#!/bin/bash
# DopeMAN - 驗證團隊結構
# 用途：檢查團隊結構的完整性與正確性

set -e

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 DopeMAN - 結構驗證"
echo "============================"
echo ""

TEAM_DIR="$HOME/DEV/Projects/dopeman"
ERRORS=0
WARNINGS=0

# 檢查函數
check_file() {
    local file=$1
    local desc=$2
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $desc"
    else
        echo -e "  ${RED}✗${NC} $desc (缺少: $file)"
        ((ERRORS++))
    fi
}

check_dir() {
    local dir=$1
    local desc=$2
    if [ -d "$dir" ]; then
        echo -e "  ${GREEN}✓${NC} $desc"
    else
        echo -e "  ${RED}✗${NC} $desc (缺少: $dir)"
        ((ERRORS++))
    fi
}

# 1. 檢查基本結構
echo "📁 檢查基本結構..."
check_file "$TEAM_DIR/CLAUDE.md" "CLAUDE.md 存在"
check_dir "$TEAM_DIR/.claude" ".claude 目錄存在"
check_dir "$TEAM_DIR/.claude/agents" "agents 目錄存在"
check_dir "$TEAM_DIR/.claude/skills" "skills 目錄存在"
check_dir "$TEAM_DIR/.claude/rules" "rules 目錄存在"
check_dir "$TEAM_DIR/commands" "commands 目錄存在"
echo ""

# 2. 檢查 Agents (6個)
echo "🤖 檢查 Agents..."
check_file "$TEAM_DIR/.claude/agents/dopeman-coordinator.md" "Coordinator (根目錄)"
check_file "$TEAM_DIR/.claude/agents/environment/file-organizer.md" "File Organizer"
check_file "$TEAM_DIR/.claude/agents/environment/sync-manager.md" "Sync Manager"
check_file "$TEAM_DIR/.claude/agents/skills-management/skill-tracker.md" "Skill Tracker"
check_file "$TEAM_DIR/.claude/agents/skills-management/skill-scout.md" "Skill Scout"
check_file "$TEAM_DIR/.claude/agents/analytics/usage-analyst.md" "Usage Analyst"
echo ""

# 3. 檢查 Shared Skills (6個)
echo "🔧 檢查 Shared Skills..."
check_file "$TEAM_DIR/.claude/skills/shared/github-api-operations/SKILL.md" "GitHub API Operations"
check_file "$TEAM_DIR/.claude/skills/shared/version-comparison/SKILL.md" "Version Comparison"
check_file "$TEAM_DIR/.claude/skills/shared/json-registry-manager/SKILL.md" "JSON Registry Manager"
check_file "$TEAM_DIR/.claude/skills/shared/file-classification/SKILL.md" "File Classification"
check_file "$TEAM_DIR/.claude/skills/shared/cross-platform-path/SKILL.md" "Cross Platform Path"
check_file "$TEAM_DIR/.claude/skills/shared/user-confirmation/SKILL.md" "User Confirmation"
echo ""

# 4. 檢查 Specialized Skills (6個)
echo "⚙️  檢查 Specialized Skills..."
check_file "$TEAM_DIR/.claude/skills/specialized/dopeman-orchestration/SKILL.md" "DopeMAN Orchestration"
check_file "$TEAM_DIR/.claude/skills/specialized/file-system-operations/SKILL.md" "File System Operations"
check_file "$TEAM_DIR/.claude/skills/specialized/skill-lineage-tracking/SKILL.md" "Skill Lineage Tracking"
check_file "$TEAM_DIR/.claude/skills/specialized/skill-discovery/SKILL.md" "Skill Discovery"
check_file "$TEAM_DIR/.claude/skills/specialized/usage-statistics/SKILL.md" "Usage Statistics"
check_file "$TEAM_DIR/.claude/skills/specialized/environment-sync/SKILL.md" "Environment Sync"
echo ""

# 5. 檢查 Rules (5個)
echo "📜 檢查 Rules..."
check_file "$TEAM_DIR/.claude/rules/no-silent-failures.md" "No Silent Failures"
check_file "$TEAM_DIR/.claude/rules/backup-before-modify.md" "Backup Before Modify"
check_file "$TEAM_DIR/.claude/rules/idempotent-operations.md" "Idempotent Operations"
check_file "$TEAM_DIR/.claude/rules/log-all-actions.md" "Log All Actions"
check_file "$TEAM_DIR/.claude/rules/respect-rate-limits.md" "Respect Rate Limits"
echo ""

# 6. 檢查 YAML frontmatter
echo "📋 檢查 YAML frontmatter..."
YAML_ERRORS=0

for agent_file in "$TEAM_DIR/.claude/agents"/**/*.md; do
    if [ -f "$agent_file" ]; then
        first_line=$(head -n 1 "$agent_file")
        if [ "$first_line" != "---" ]; then
            echo -e "  ${RED}✗${NC} $(basename $agent_file) - 缺少 YAML frontmatter"
            ((YAML_ERRORS++))
        fi
    fi
done

if [ $YAML_ERRORS -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} 所有 agents YAML frontmatter 正確"
else
    echo -e "  ${YELLOW}⚠${NC}  $YAML_ERRORS 個檔案 YAML frontmatter 有問題"
    ((WARNINGS+=$YAML_ERRORS))
fi
echo ""

# 7. 檢查 Commands
echo "⚡ 檢查 Commands..."
check_file "$TEAM_DIR/commands/README.md" "Commands README"
check_file "$TEAM_DIR/commands/init-registry.sh" "init-registry.sh"
check_file "$TEAM_DIR/commands/check-updates.sh" "check-updates.sh"
check_file "$TEAM_DIR/commands/validate-structure.sh" "validate-structure.sh (本身)"

# 檢查執行權限
if [ -x "$TEAM_DIR/commands/init-registry.sh" ]; then
    echo -e "  ${GREEN}✓${NC} 腳本有執行權限"
else
    echo -e "  ${YELLOW}⚠${NC}  腳本缺少執行權限 (執行: chmod +x commands/*.sh)"
    ((WARNINGS++))
fi
echo ""

# 總結
echo "="*50
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ 驗證通過！結構完整無誤。${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  驗證完成，有 $WARNINGS 個警告。${NC}"
    exit 0
else
    echo -e "${RED}❌ 驗證失敗！發現 $ERRORS 個錯誤，$WARNINGS 個警告。${NC}"
    exit 1
fi
