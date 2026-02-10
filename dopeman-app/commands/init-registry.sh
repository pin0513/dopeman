#!/bin/bash
# DopeMAN - 初始化 Registry
# 用途：第一次使用時初始化資料結構

set -e  # 遇到錯誤立即停止

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 DopeMAN Registry 初始化"
echo "================================"
echo ""

# 設定路徑
MEMORY_DIR="$HOME/.claude/memory/dopeman"
SKILLS_DIR="$HOME/.claude/skills"

# 1. 創建目錄結構
echo "📁 創建目錄結構..."
mkdir -p "$MEMORY_DIR"
mkdir -p "$MEMORY_DIR/backups"
mkdir -p "$MEMORY_DIR/reports"

# 2. 初始化 skills-registry.json
echo "📋 初始化 skills registry..."
REGISTRY_FILE="$MEMORY_DIR/skills-registry.json"

if [ -f "$REGISTRY_FILE" ]; then
    echo -e "${YELLOW}⚠️  Registry 已存在，備份到 .backup${NC}"
    cp "$REGISTRY_FILE" "$MEMORY_DIR/backups/skills-registry.$(date +%Y%m%d_%H%M%S).backup.json"
fi

cat > "$REGISTRY_FILE" << 'EOF'
{
  "version": "1.0.0",
  "last_updated": "",
  "skills": []
}
EOF

# 3. 掃描現有 skills
echo "🔍 掃描現有 skills..."
SKILL_COUNT=0

if [ -d "$SKILLS_DIR" ]; then
    # 使用 Python 處理 JSON（更可靠）
    python3 << PYTHON_SCRIPT
import json
import os
from datetime import datetime
from pathlib import Path

skills_dir = Path("$SKILLS_DIR")
registry_file = "$REGISTRY_FILE"

# 載入現有 registry
with open(registry_file, 'r') as f:
    registry = json.load(f)

# 掃描 skills
skills = []
for skill_path in skills_dir.rglob("SKILL.md"):
    skill_name = skill_path.parent.name
    relative_path = str(skill_path.parent.relative_to(Path.home()))

    # 嘗試解析來源（從 SKILL.md 的 YAML frontmatter 或註解）
    source = "local"
    version = "unknown"

    skills.append({
        "name": skill_name,
        "path": f"~/{relative_path}",
        "source": source,
        "version": version,
        "installed_at": datetime.now().isoformat(),
        "forked_from": None,
        "local_modifications": [],
        "used_by": [],
        "last_used": None,
        "has_update": False
    })

registry["skills"] = skills
registry["last_updated"] = datetime.now().isoformat()

# 寫回檔案
with open(registry_file, 'w') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

print(f"✓ 已掃描 {len(skills)} 個 skills")
PYTHON_SCRIPT

    SKILL_COUNT=$(python3 -c "import json; print(len(json.load(open('$REGISTRY_FILE'))['skills']))")
fi

# 4. 初始化其他檔案
echo "📝 初始化其他資料檔案..."

# skill-recommendations.json
cat > "$MEMORY_DIR/skill-recommendations.json" << 'EOF'
{
  "last_checked": "",
  "recommendations": []
}
EOF

# usage-report.json
cat > "$MEMORY_DIR/usage-report.json" << 'EOF'
{
  "period": "30days",
  "generated_at": "",
  "top_skills": [],
  "unused_skills": [],
  "project_breakdown": {}
}
EOF

# github-cache.json
cat > "$MEMORY_DIR/github-cache.json" << 'EOF'
{
  "cache": {}
}
EOF

# operation.log
touch "$MEMORY_DIR/operation.log"
echo "[$(date -Iseconds)] [init] DopeMAN registry initialized" >> "$MEMORY_DIR/operation.log"

# 5. 完成報告
echo ""
echo -e "${GREEN}✅ 初始化完成！${NC}"
echo ""
echo "📊 摘要："
echo "  - Memory 目錄: $MEMORY_DIR"
echo "  - 已掃描 Skills: $SKILL_COUNT 個"
echo "  - Registry 檔案: $REGISTRY_FILE"
echo ""
echo "🔧 下一步："
echo "  1. 執行 ./check-updates.sh 檢查更新"
echo "  2. 執行 ./usage-report.sh 查看使用報告"
echo "  3. 執行 ./discover-skills.sh 探索新 skills"
echo ""
