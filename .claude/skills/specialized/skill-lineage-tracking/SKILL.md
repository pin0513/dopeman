---
name: Skill Lineage Tracking
description: 追蹤 skill 的來源、版本歷史、upstream 關係
---

# Skill Lineage Tracking

## 描述

維護每個 skill 的完整血緣資訊，包括 upstream repo、fork 歷史、版本變更、customization 記錄。

## 使用者

- **skill-tracker**：唯一使用者，追蹤 skills 的來源與更新

## 核心知識

### Lineage 資訊結構

```json
{
  "skill_name": "github-api-operations",
  "lineage": {
    "source": "upstream",
    "upstream_repo": "anthropics/claude-code",
    "upstream_path": "skills/developer/github-api-operations/SKILL.md",
    "fork_date": "2026-01-15T10:00:00Z",
    "original_version": "v1.0.0",
    "current_version": "v1.2.0",
    "customizations": [
      {
        "date": "2026-01-20T14:30:00Z",
        "type": "enhancement",
        "description": "Added rate limit handling",
        "author": "paul_huang"
      }
    ],
    "upstream_commits": [
      {
        "sha": "abc123",
        "date": "2026-01-10T09:00:00Z",
        "message": "Initial version",
        "synced": true
      },
      {
        "sha": "def456",
        "date": "2026-02-05T11:00:00Z",
        "message": "Added error handling",
        "synced": false
      }
    ]
  }
}
```

### Skill 類型判定

| Source | 特徵 | 處理方式 |
|--------|------|---------|
| **upstream** | 有 upstream_repo 欄位 | 可同步更新 |
| **forked** | 有 upstream 但有 customizations | 需手動 merge |
| **custom** | 無 upstream_repo | 不同步，本地維護 |

## 範例

### 初始化 Lineage

```bash
init_lineage() {
  local skill_name="$1"
  local upstream_repo="$2"
  local upstream_path="$3"

  # 取得最新 commit
  latest_commit=$(gh api "repos/$upstream_repo/commits?path=$upstream_path" --jq '.[0].sha')
  commit_date=$(gh api "repos/$upstream_repo/commits/$latest_commit" --jq '.commit.author.date')

  # 建立 lineage 記錄
  jq ".skills[\"$skill_name\"].lineage = {
    \"source\": \"upstream\",
    \"upstream_repo\": \"$upstream_repo\",
    \"upstream_path\": \"$upstream_path\",
    \"fork_date\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
    \"current_version\": \"v1.0.0\",
    \"customizations\": [],
    \"upstream_commits\": [{
      \"sha\": \"$latest_commit\",
      \"date\": \"$commit_date\",
      \"message\": \"Initial fork\",
      \"synced\": true
    }]
  }" skills_registry.json > skills_registry.json.tmp \
    && mv skills_registry.json.tmp skills_registry.json

  echo "✅ Initialized lineage for: $skill_name"
}

# 使用範例
init_lineage "github-api-operations" \
             "anthropics/claude-code" \
             "skills/developer/github-api-operations/SKILL.md"
```

### 檢查 Upstream 更新

```bash
check_upstream_updates() {
  local skill_name="$1"

  # 讀取 lineage 資訊
  upstream_repo=$(jq -r ".skills[\"$skill_name\"].lineage.upstream_repo" skills_registry.json)
  upstream_path=$(jq -r ".skills[\"$skill_name\"].lineage.upstream_path" skills_registry.json)
  local_commit=$(jq -r ".skills[\"$skill_name\"].lineage.upstream_commits[-1].sha" skills_registry.json)

  if [ "$upstream_repo" == "null" ]; then
    echo "⚠️  No upstream configured for: $skill_name"
    return 1
  fi

  # 取得最新 commit
  latest_commit=$(gh api "repos/$upstream_repo/commits?path=$upstream_path" --jq '.[0].sha')

  if [ "$local_commit" == "$latest_commit" ]; then
    echo "✅ $skill_name is up-to-date"
    return 0
  else
    echo "⚠️  $skill_name has updates available"
    echo "   Local:    $local_commit"
    echo "   Upstream: $latest_commit"

    # 取得中間的 commits
    commits=$(gh api "repos/$upstream_repo/commits?path=$upstream_path" \
      --jq ".[] | select(.sha != \"$local_commit\") | {sha: .sha, date: .commit.author.date, message: .commit.message}")

    echo ""
    echo "New commits:"
    echo "$commits" | jq -r '"\(.date) - \(.message)"'

    return 2
  fi
}

# 使用範例
check_upstream_updates "github-api-operations"
```

### 記錄 Customization

```bash
record_customization() {
  local skill_name="$1"
  local type="$2"  # enhancement, bugfix, breaking-change
  local description="$3"

  jq ".skills[\"$skill_name\"].lineage.customizations += [{
    \"date\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
    \"type\": \"$type\",
    \"description\": \"$description\",
    \"author\": \"$(whoami)\"
  }]" skills_registry.json > skills_registry.json.tmp \
    && mv skills_registry.json.tmp skills_registry.json

  # 標記為 forked
  jq ".skills[\"$skill_name\"].lineage.source = \"forked\"" \
    skills_registry.json > skills_registry.json.tmp \
    && mv skills_registry.json.tmp skills_registry.json

  echo "✅ Recorded customization for: $skill_name"
}

# 使用範例
record_customization "github-api-operations" \
                     "enhancement" \
                     "Added support for GitHub Enterprise"
```

### 生成 Lineage 報告

```bash
generate_lineage_report() {
  local skill_name="$1"

  lineage=$(jq ".skills[\"$skill_name\"].lineage" skills_registry.json)

  cat << EOF
╔════════════════════════════════════════╗
║   Skill Lineage Report                 ║
╚════════════════════════════════════════╝

Skill: $skill_name

┌─ Source ─────────────────────────────────
│ Type: $(echo "$lineage" | jq -r '.source')
│ Upstream: $(echo "$lineage" | jq -r '.upstream_repo')
│ Path: $(echo "$lineage" | jq -r '.upstream_path')
│ Forked: $(echo "$lineage" | jq -r '.fork_date')
└──────────────────────────────────────────

┌─ Versions ───────────────────────────────
│ Original: $(echo "$lineage" | jq -r '.original_version')
│ Current:  $(echo "$lineage" | jq -r '.current_version')
└──────────────────────────────────────────

┌─ Customizations ─────────────────────────
$(echo "$lineage" | jq -r '.customizations[] | "│ \(.date) - \(.type): \(.description)"')
└──────────────────────────────────────────

┌─ Upstream Commits ───────────────────────
$(echo "$lineage" | jq -r '.upstream_commits[] | "│ \(.sha[0:7]) \(if .synced then "✅" else "⏸️" end) \(.date) - \(.message)"')
└──────────────────────────────────────────

EOF
}

# 使用範例
generate_lineage_report "github-api-operations"
```

### 比較 Local 與 Upstream

```bash
diff_with_upstream() {
  local skill_name="$1"
  local local_path=$(jq -r ".skills[\"$skill_name\"].path" skills_registry.json)
  local upstream_repo=$(jq -r ".skills[\"$skill_name\"].lineage.upstream_repo" skills_registry.json)
  local upstream_path=$(jq -r ".skills[\"$skill_name\"].lineage.upstream_path" skills_registry.json)

  # 下載 upstream 版本
  gh api "repos/$upstream_repo/contents/$upstream_path" \
    --jq '.content' | base64 -d > /tmp/upstream_version.md

  # 比對
  echo "📊 Comparing local vs upstream..."
  diff -u /tmp/upstream_version.md "$HOME/.claude/$local_path" || true

  rm /tmp/upstream_version.md
}

# 使用範例
diff_with_upstream "github-api-operations"
```

### 批次檢查所有 Upstream Skills

```bash
check_all_upstream_skills() {
  echo "🔍 Checking all upstream skills..."
  echo ""

  # 找出所有 upstream skills
  skills=$(jq -r '.skills | to_entries[] | select(.value.lineage.source == "upstream") | .key' skills_registry.json)

  local total=0
  local outdated=0

  for skill in $skills; do
    ((total++))
    if check_upstream_updates "$skill"; then
      # up-to-date
      :
    else
      ((outdated++))
    fi
    echo ""
  done

  echo "────────────────────────────────────────"
  echo "Total upstream skills: $total"
  echo "Outdated: $outdated"
  echo "Up-to-date: $((total - outdated))"
}
```

## 相關規則

- `rules/versioning-strategy.md`：版本號管理策略
- `rules/customization-tracking.md`：記錄 customization 的規範
- `rules/upstream-sync-policy.md`：何時同步 upstream 更新
- `rules/no-silent-failures.md`：lineage 更新失敗必須記錄
