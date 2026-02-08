---
name: JSON Registry Manager
description: 讀寫 skills_registry.json，維護 skill 元數據
---

# JSON Registry Manager

## 描述

提供 `skills_registry.json` 的讀寫、查詢、更新操作，確保 JSON 格式正確且操作原子性。

## 使用者

- **skill-tracker**：記錄 upstream commit hash、最後檢查時間
- **usage-analyst**：記錄 skill 使用次數、最後使用時間
- **sync-manager**：標記同步狀態、衝突資訊
- **coordinator**：讀取 registry 決定派工

## 核心知識

### Registry 結構

```json
{
  "skills": {
    "skill-name": {
      "source": "upstream" | "custom",
      "path": "skills/shared/skill-name/SKILL.md",
      "upstream_repo": "owner/repo",
      "upstream_path": "path/in/repo/SKILL.md",
      "version": "v1.2.3",
      "last_commit": "abc123def456",
      "last_checked": "2026-02-08T10:30:00Z",
      "last_synced": "2026-02-08T09:00:00Z",
      "sync_status": "up-to-date" | "outdated" | "conflict" | "custom",
      "usage_count": 42,
      "last_used": "2026-02-08T15:45:00Z",
      "used_by_agents": ["agent-1", "agent-2"]
    }
  },
  "last_updated": "2026-02-08T16:00:00Z"
}
```

### 操作原則

1. **讀取前先備份**：避免寫入失敗導致資料遺失
2. **寫入後驗證**：確保 JSON 格式正確
3. **使用檔案鎖**：避免並發寫入衝突
4. **記錄變更歷史**：重要變更應寫入 CHANGELOG

## 範例

### 讀取 Skill 資訊

```bash
# 使用 jq 讀取
skill_name="github-api-operations"
jq -r ".skills[\"$skill_name\"]" skills_registry.json
```

### 更新單一欄位

```bash
# 更新最後檢查時間
skill_name="github-api-operations"
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

jq ".skills[\"$skill_name\"].last_checked = \"$timestamp\"" \
  skills_registry.json > skills_registry.json.tmp \
  && mv skills_registry.json.tmp skills_registry.json
```

### 新增 Skill

```bash
# 新增或更新 skill
skill_name="new-skill"
jq ".skills[\"$skill_name\"] = {
  \"source\": \"custom\",
  \"path\": \"skills/custom/$skill_name/SKILL.md\",
  \"version\": \"v1.0.0\",
  \"last_commit\": \"initial\",
  \"sync_status\": \"custom\",
  \"usage_count\": 0
}" skills_registry.json > skills_registry.json.tmp \
  && mv skills_registry.json.tmp skills_registry.json
```

### 查詢過期 Skills

```bash
# 找出 sync_status = "outdated" 的 skills
jq -r '.skills | to_entries[] | select(.value.sync_status == "outdated") | .key' \
  skills_registry.json
```

### 統計 Usage

```bash
# 找出最常用的 5 個 skills
jq -r '.skills | to_entries | sort_by(-.value.usage_count) | .[0:5] | .[] | "\(.key): \(.value.usage_count)"' \
  skills_registry.json
```

## 錯誤處理

### JSON 格式錯誤

```bash
# 驗證 JSON 格式
if ! jq empty skills_registry.json 2>/dev/null; then
  echo "❌ Invalid JSON format in skills_registry.json"
  # 從備份還原
  if [ -f skills_registry.json.backup ]; then
    cp skills_registry.json.backup skills_registry.json
  fi
fi
```

### 並發寫入保護

```bash
# 使用檔案鎖
lockfile="skills_registry.json.lock"

# 取得鎖
exec 200>"$lockfile"
flock -n 200 || { echo "Registry is locked by another process"; exit 1; }

# 執行操作
jq ".skills[\"$skill_name\"].last_checked = \"$timestamp\"" \
  skills_registry.json > skills_registry.json.tmp \
  && mv skills_registry.json.tmp skills_registry.json

# 釋放鎖
flock -u 200
```

## 相關規則

- `rules/atomic-registry-updates.md`：確保 registry 更新的原子性
- `rules/no-silent-failures.md`：JSON 解析錯誤必須記錄
- `rules/registry-backup-policy.md`：備份策略與還原機制
