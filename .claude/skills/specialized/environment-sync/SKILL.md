---
name: Environment Sync
description: 同步 skills/agents 到不同環境（~/DEV 與 ~/teams）
---

# Environment Sync

## 描述

管理 .claude 目錄在不同環境間的同步，包括 ~/DEV 與 ~/teams/dopeman，確保 skills 與 agents 版本一致。

## 使用者

- **sync-manager**：唯一使用者，負責環境同步任務

## 核心知識

### 環境定義

| 環境 | 路徑 | 用途 |
|------|------|------|
| **Global** | `~/.claude/` | 全域設定、通用 rules |
| **Project** | `~/DEV/{project}/.claude/` | 專案特定設定 |
| **Team** | `~/teams/{team}/.claude/` | 團隊共享 skills/agents |

### 同步策略

| 檔案類型 | 同步方向 | 衝突處理 |
|---------|---------|---------|
| Shared Skills | Team → Projects | 版本較新者勝出 |
| Specialized Skills | 不同步（專屬） | - |
| Rules | Team ← Projects | 手動 merge |
| Agents | Team → Projects | 版本較新者勝出 |
| Registry | Team ← Projects | 合併使用次數 |

### 衝突類型

1. **版本衝突**：同一 skill 兩邊版本不同
2. **內容衝突**：同版本但內容不同（customization）
3. **路徑衝突**：檔案位置不一致

## 範例

### 掃描環境差異

```bash
scan_environments() {
  local team_dir="$HOME/teams/dopeman/.claude"
  local project_dir="$HOME/DEV/MAYO-Report-Master/.claude"

  echo "🔍 Scanning environments..."
  echo ""

  # 比對 skills
  echo "┌─ Shared Skills ─────────────────────"

  team_skills=$(find "$team_dir/skills/shared" -name "SKILL.md" 2>/dev/null | sed "s|$team_dir/skills/shared/||" | sed 's|/SKILL.md||' | sort)
  project_skills=$(find "$project_dir/skills/shared" -name "SKILL.md" 2>/dev/null | sed "s|$project_dir/skills/shared/||" | sed 's|/SKILL.md||' | sort)

  # 找出差異
  only_in_team=$(comm -23 <(echo "$team_skills") <(echo "$project_skills"))
  only_in_project=$(comm -13 <(echo "$team_skills") <(echo "$project_skills"))
  common=$(comm -12 <(echo "$team_skills") <(echo "$project_skills"))

  echo "│ In team only: $(echo "$only_in_team" | wc -l | tr -d ' ')"
  for skill in $only_in_team; do
    echo "│   - $skill"
  done

  echo "│"
  echo "│ In project only: $(echo "$only_in_project" | wc -l | tr -d ' ')"
  for skill in $only_in_project; do
    echo "│   - $skill"
  done

  echo "│"
  echo "│ Common: $(echo "$common" | wc -l | tr -d ' ')"
  echo "└─────────────────────────────────────"

  # 比對版本
  echo ""
  echo "┌─ Version Differences ───────────────"
  for skill in $common; do
    team_version=$(grep -E '^version:' "$team_dir/skills/shared/$skill/SKILL.md" 2>/dev/null | awk '{print $2}')
    project_version=$(grep -E '^version:' "$project_dir/skills/shared/$skill/SKILL.md" 2>/dev/null | awk '{print $2}')

    if [ "$team_version" != "$project_version" ]; then
      echo "│ ⚠️  $skill"
      echo "│   Team: $team_version"
      echo "│   Project: $project_version"
    fi
  done
  echo "└─────────────────────────────────────"
}

# 使用範例
scan_environments
```

### 同步 Skill

```bash
sync_skill() {
  local skill_name="$1"
  local direction="$2"  # team-to-project 或 project-to-team
  local team_dir="$HOME/teams/dopeman/.claude"
  local project_dir="$HOME/DEV/MAYO-Report-Master/.claude"

  case "$direction" in
    team-to-project)
      source="$team_dir/skills/shared/$skill_name/SKILL.md"
      dest="$project_dir/skills/shared/$skill_name/SKILL.md"
      ;;
    project-to-team)
      source="$project_dir/skills/shared/$skill_name/SKILL.md"
      dest="$team_dir/skills/shared/$skill_name/SKILL.md"
      ;;
    *)
      echo "❌ Invalid direction: $direction"
      return 1
      ;;
  esac

  # 驗證來源存在
  if [ ! -f "$source" ]; then
    echo "❌ Source not found: $source"
    return 1
  fi

  # 比對版本
  source_version=$(grep -E '^version:' "$source" | awk '{print $2}')
  dest_version=$(grep -E '^version:' "$dest" 2>/dev/null | awk '{print $2}')

  echo "Syncing: $skill_name ($direction)"
  echo "  Source version: $source_version"
  echo "  Dest version: $dest_version"

  # 確認
  if [ -f "$dest" ]; then
    echo -n "Overwrite destination? (y/N): "
    read -r response
    case "$response" in
      [yY]|[yY][eE][sS])
        ;;
      *)
        echo "❌ Cancelled"
        return 1
        ;;
    esac
  fi

  # 確保目標目錄存在
  dest_dir=$(dirname "$dest")
  mkdir -p "$dest_dir"

  # 複製
  if cp "$source" "$dest"; then
    echo "✅ Synced: $skill_name"
    return 0
  else
    echo "❌ Failed to sync"
    return 1
  fi
}

# 使用範例
sync_skill "github-api-operations" "team-to-project"
```

### 批次同步

```bash
batch_sync() {
  local direction="$1"
  local team_dir="$HOME/teams/dopeman/.claude"
  local project_dir="$HOME/DEV/MAYO-Report-Master/.claude"

  case "$direction" in
    team-to-project)
      source_dir="$team_dir/skills/shared"
      ;;
    project-to-team)
      source_dir="$project_dir/skills/shared"
      ;;
    *)
      echo "❌ Invalid direction"
      return 1
      ;;
  esac

  # 找出所有 skills
  skills=$(find "$source_dir" -name "SKILL.md" 2>/dev/null | sed "s|$source_dir/||" | sed 's|/SKILL.md||' | sort)

  total=$(echo "$skills" | wc -l | tr -d ' ')
  echo "📦 Batch sync: $total skills ($direction)"
  echo ""

  # 確認
  echo -n "Proceed? (y/N): "
  read -r response
  case "$response" in
    [yY]|[yY][eE][sS])
      ;;
    *)
      echo "❌ Cancelled"
      return 1
      ;;
  esac

  # 執行同步
  local success=0
  for skill in $skills; do
    if sync_skill "$skill" "$direction"; then
      ((success++))
    fi
    echo ""
  done

  echo "────────────────────────────────────────"
  echo "Synced: $success/$total"
}

# 使用範例
batch_sync "team-to-project"
```

### 衝突檢測

```bash
detect_conflicts() {
  local team_dir="$HOME/teams/dopeman/.claude"
  local project_dir="$HOME/DEV/MAYO-Report-Master/.claude"

  echo "🔍 Detecting conflicts..."
  echo ""

  # 找出共同 skills
  team_skills=$(find "$team_dir/skills/shared" -name "SKILL.md" 2>/dev/null | sed "s|$team_dir/skills/shared/||" | sed 's|/SKILL.md||' | sort)
  project_skills=$(find "$project_dir/skills/shared" -name "SKILL.md" 2>/dev/null | sed "s|$project_dir/skills/shared/||" | sed 's|/SKILL.md||' | sort)
  common=$(comm -12 <(echo "$team_skills") <(echo "$project_skills"))

  local conflicts=0

  for skill in $common; do
    team_file="$team_dir/skills/shared/$skill/SKILL.md"
    project_file="$project_dir/skills/shared/$skill/SKILL.md"

    team_version=$(grep -E '^version:' "$team_file" | awk '{print $2}')
    project_version=$(grep -E '^version:' "$project_file" | awk '{print $2}')

    # 版本相同但內容不同 = 衝突
    if [ "$team_version" == "$project_version" ]; then
      if ! diff -q "$team_file" "$project_file" >/dev/null 2>&1; then
        echo "🔴 CONFLICT: $skill"
        echo "   Same version ($team_version) but different content"
        echo "   Diff:"
        diff -u "$team_file" "$project_file" | head -20
        echo ""
        ((conflicts++))
      fi
    fi
  done

  if [ $conflicts -eq 0 ]; then
    echo "✅ No conflicts detected"
  else
    echo "────────────────────────────────────────"
    echo "Total conflicts: $conflicts"
  fi
}

# 使用範例
detect_conflicts
```

### 合併 Registry

```bash
merge_registries() {
  local team_registry="$HOME/teams/dopeman/.claude/skills_registry.json"
  local project_registry="$HOME/DEV/MAYO-Report-Master/.claude/skills_registry.json"
  local merged_registry="/tmp/merged_registry.json"

  echo "🔀 Merging registries..."
  echo ""

  # 使用 jq 合併
  jq -s '
    reduce .[] as $item (
      {};
      . * $item |
      .skills = (
        ($item.skills // {}) + (.skills // {}) |
        to_entries |
        group_by(.key) |
        map({
          key: .[0].key,
          value: (
            .[0].value + .[1].value |
            .usage_count = ([.[].usage_count] | add) |
            .last_used = ([.[].last_used] | max)
          )
        }) |
        from_entries
      )
    )
  ' "$team_registry" "$project_registry" > "$merged_registry"

  echo "✅ Merged registry saved to: $merged_registry"
  echo ""
  echo "Review and manually copy to team/project as needed."
}

# 使用範例
merge_registries
```

## 輸出格式

### 同步報告

```
📦 Environment Sync Report

Direction: Team → Project
Date: 2026-02-08 16:00:00

┌─ Summary ───────────────────────────────
│ Total skills: 12
│ Synced: 10
│ Skipped: 2
│ Conflicts: 0
└─────────────────────────────────────────

┌─ Synced Skills ─────────────────────────
│ ✅ github-api-operations (v1.2.0)
│ ✅ version-comparison (v1.1.0)
│ ✅ json-registry-manager (v2.0.0)
│ ... (7 more)
└─────────────────────────────────────────

┌─ Skipped ───────────────────────────────
│ ⏸️  custom-tool (user declined)
│ ⏸️  experimental-feature (destination newer)
└─────────────────────────────────────────
```

### 衝突警告

```
🔴 CONFLICT DETECTED

Skill: github-api-operations
Version: v1.2.0 (both environments)

Team environment:
  - Added rate limit handling
  - Modified: 2026-02-07

Project environment:
  - Added retry logic
  - Modified: 2026-02-08

Action required: Manual merge needed
```

## 相關規則

- `rules/sync-conflict-resolution.md`：衝突解決策略
- `rules/environment-isolation.md`：哪些檔案不應同步
- `rules/backup-before-sync.md`：同步前備份策略
- `rules/no-silent-failures.md`：同步錯誤必須記錄
