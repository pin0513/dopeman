#!/bin/bash
# DopeThingsMan - 檢查 Skills 更新
# 用途：檢查所有 skills 是否有新版本可用

set -e

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔍 DopeThingsMan - 檢查 Skills 更新"
echo "===================================="
echo ""

# 檢查依賴
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ 錯誤：找不到 gh CLI${NC}"
    echo "請安裝：brew install gh"
    exit 1
fi

# 路徑設定
REGISTRY_FILE="$HOME/.claude/memory/dopethingsman/skills-registry.json"

if [ ! -f "$REGISTRY_FILE" ]; then
    echo -e "${RED}❌ Registry 不存在${NC}"
    echo "請先執行：./init-registry.sh"
    exit 1
fi

echo "📋 載入 registry..."
SKILL_COUNT=$(python3 -c "import json; print(len(json.load(open('$REGISTRY_FILE'))['skills']))")
echo "   找到 $SKILL_COUNT 個 skills"
echo ""

# 檢查更新
echo "🔎 檢查 GitHub upstream..."
python3 << 'PYTHON_SCRIPT'
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path

registry_file = "$REGISTRY_FILE"

# 載入 registry
with open(registry_file, 'r') as f:
    registry = json.load(f)

updates_found = 0
errors = []

for skill in registry['skills']:
    name = skill['name']
    source = skill.get('source', 'local')
    current_version = skill.get('version', 'unknown')

    # 跳過 local skills
    if source == 'local' or not source.startswith('http'):
        continue

    print(f"⏳ 檢查 {name}...", end=' ', flush=True)

    try:
        # 解析 GitHub repo URL
        match = re.match(r'https://github.com/([^/]+)/([^/]+)', source)
        if not match:
            print("⏭️  跳過（非 GitHub repo）")
            continue

        owner, repo = match.groups()
        repo = repo.replace('.git', '')

        # 使用 gh CLI 取得最新 release
        result = subprocess.run(
            ['gh', 'api', f'repos/{owner}/{repo}/releases/latest'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            # 嘗試取得最新 commit
            result = subprocess.run(
                ['gh', 'api', f'repos/{owner}/{repo}/commits/main'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                latest_version = data['sha'][:7]
            else:
                print("⚠️  無法取得版本")
                continue
        else:
            data = json.loads(result.stdout)
            latest_version = data['tag_name']

        # 比較版本
        if latest_version != current_version:
            print(f"🔔 有更新 ({current_version} → {latest_version})")
            skill['has_update'] = True
            skill['update_info'] = {
                'upstream_version': latest_version,
                'checked_at': datetime.now().isoformat()
            }
            updates_found += 1
        else:
            print("✅ 已是最新")
            skill['has_update'] = False

    except subprocess.TimeoutExpired:
        print("⏱️  逾時")
        errors.append(f"{name}: 請求逾時")
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        errors.append(f"{name}: {str(e)}")

# 更新 registry
registry['last_updated'] = datetime.now().isoformat()
with open(registry_file, 'w') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

# 摘要
print("")
print("="*50)
if updates_found > 0:
    print(f"🔔 發現 {updates_found} 個 skills 有更新可用")
else:
    print("✅ 所有 skills 都是最新版本")

if errors:
    print(f"⚠️  {len(errors)} 個 skills 檢查失敗")

PYTHON_SCRIPT

echo ""
echo "📊 詳細報告已儲存到 registry"
echo "   查看：cat $REGISTRY_FILE | jq '.skills[] | select(.has_update == true)'"
echo ""
