---
name: Usage Statistics
description: 統計 skill 使用頻率、產生分析報告
---

# Usage Statistics

## 描述

追蹤每個 skill 的使用次數、最後使用時間、被哪些 agents 使用，產生統計報告協助決策。

## 使用者

- **usage-analyst**：唯一使用者，負責分析 skill 使用狀況

## 核心知識

### 統計維度

| 維度 | 資料來源 | 用途 |
|------|---------|------|
| 使用次數 | skills_registry.json | 識別熱門/冷門 skills |
| 最後使用時間 | skills_registry.json | 識別廢棄 skills |
| 使用者 Agent | Agent .md 檔案掃描 | 了解依賴關係 |
| 版本分佈 | skills_registry.json | 識別過時版本 |
| 來源類型 | skills_registry.json | upstream vs custom 比例 |

### 報告類型

1. **熱門 Skills 排行**：找出最常用的 skills
2. **冷門 Skills 清單**：找出可移除的 skills
3. **依賴關係圖**：哪些 agents 依賴哪些 skills
4. **版本健康度**：skills 的版本分佈
5. **來源分析**：upstream vs custom skills 比例

## 範例

### 統計使用次數

```bash
calculate_usage_stats() {
  local registry="$HOME/.claude/skills_registry.json"

  echo "📊 Calculating usage statistics..."
  echo ""

  # 總計
  total_skills=$(jq '.skills | length' "$registry")
  upstream_skills=$(jq '[.skills[] | select(.source == "upstream")] | length' "$registry")
  custom_skills=$(jq '[.skills[] | select(.source == "custom")] | length' "$registry")

  echo "Total skills: $total_skills"
  echo "  - Upstream: $upstream_skills"
  echo "  - Custom: $custom_skills"
  echo ""

  # 計算總使用次數
  total_usage=$(jq '[.skills[].usage_count // 0] | add' "$registry")
  echo "Total usage count: $total_usage"
  echo ""

  # 最常用的 5 個
  echo "Top 5 most used skills:"
  jq -r '.skills | to_entries | sort_by(-.value.usage_count) | .[0:5] | .[] | "  \(.value.usage_count)x - \(.key)"' "$registry"
  echo ""

  # 從未使用的
  unused=$(jq -r '[.skills | to_entries[] | select(.value.usage_count == 0 or .value.usage_count == null) | .key] | length' "$registry")
  echo "Unused skills: $unused"
}

# 使用範例
calculate_usage_stats
```

### 識別廢棄 Skills

```bash
find_abandoned_skills() {
  local days_threshold="${1:-90}"  # 預設 90 天未使用
  local registry="$HOME/.claude/skills_registry.json"

  echo "🔍 Finding skills unused for $days_threshold days..."
  echo ""

  # 計算時間閾值
  threshold_date=$(date -u -v-${days_threshold}d +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -d "$days_threshold days ago" +"%Y-%m-%dT%H:%M:%SZ")

  # 找出廢棄 skills
  abandoned=$(jq -r --arg threshold "$threshold_date" '
    .skills | to_entries[] |
    select(
      (.value.last_used == null) or
      (.value.last_used < $threshold)
    ) | .key
  ' "$registry")

  if [ -z "$abandoned" ]; then
    echo "✅ No abandoned skills found"
    return
  fi

  echo "⚠️  Abandoned skills:"
  for skill in $abandoned; do
    last_used=$(jq -r ".skills[\"$skill\"].last_used" "$registry")
    usage_count=$(jq -r ".skills[\"$skill\"].usage_count // 0" "$registry")

    if [ "$last_used" == "null" ]; then
      last_used="Never"
    fi

    echo "  - $skill"
    echo "    Last used: $last_used"
    echo "    Total usage: $usage_count"
    echo ""
  done

  echo "Consider removing these skills if no longer needed."
}

# 使用範例
find_abandoned_skills 90
```

### 掃描 Agent 依賴

```bash
scan_agent_dependencies() {
  local agents_dir="$HOME/.claude/agents"
  local temp_file="/tmp/agent_dependencies.json"

  echo "🔍 Scanning agent dependencies..."
  echo ""

  # 初始化結果
  echo '{"dependencies": {}}' > "$temp_file"

  # 掃描所有 agents
  find "$agents_dir" -name "*.md" -type f | while read agent_file; do
    agent_name=$(basename "$agent_file" .md)

    echo "Scanning: $agent_name"

    # 提取 skill 引用（尋找 skills/ 路徑）
    skills=$(grep -oE 'skills/(shared|specialized)/[^/]+' "$agent_file" | sed 's|skills/[^/]*/||' | sort -u)

    if [ -z "$skills" ]; then
      continue
    fi

    # 加入結果
    for skill in $skills; do
      jq ".dependencies[\"$skill\"] += [\"$agent_name\"]" "$temp_file" > "$temp_file.tmp" \
        && mv "$temp_file.tmp" "$temp_file"
    done
  done

  echo ""
  echo "✅ Dependency scan completed"
  echo "Results saved to: $temp_file"
}

# 使用範例
scan_agent_dependencies
```

### 生成依賴關係圖

```bash
generate_dependency_graph() {
  local temp_file="/tmp/agent_dependencies.json"

  cat << 'EOF'
╔════════════════════════════════════════╗
║   Skill Dependency Graph               ║
╚════════════════════════════════════════╝

EOF

  jq -r '
    .dependencies | to_entries[] |
    "Skill: \(.key)\n  Used by: \(.value | join(", "))\n"
  ' "$temp_file"
}

# 使用範例
generate_dependency_graph
```

### 版本健康度檢查

```bash
check_version_health() {
  local registry="$HOME/.claude/skills_registry.json"

  echo "🏥 Checking version health..."
  echo ""

  # 檢查 upstream skills 的版本狀態
  jq -r '.skills | to_entries[] | select(.value.source == "upstream") |
    "\(.key)|\(.value.version // "unknown")|\(.value.sync_status // "unknown")"
  ' "$registry" | while IFS='|' read skill version status; do

    case "$status" in
      up-to-date)
        echo "✅ $skill: $version (up-to-date)"
        ;;
      outdated)
        echo "⚠️  $skill: $version (outdated)"
        ;;
      conflict)
        echo "🔴 $skill: $version (conflict)"
        ;;
      *)
        echo "❓ $skill: $version (unknown)"
        ;;
    esac
  done
}

# 使用範例
check_version_health
```

### 生成完整統計報告

```bash
generate_full_report() {
  local registry="$HOME/.claude/skills_registry.json"
  local report_file="$HOME/.claude/usage_report_$(date +%Y%m%d).md"

  cat << EOF > "$report_file"
# DopeThingsMan Usage Report

Generated: $(date)

---

## Overview

$(calculate_usage_stats | sed 's/^//')

---

## Top Used Skills

$(jq -r '.skills | to_entries | sort_by(-.value.usage_count) | .[0:10] | .[] | "- **\(.key)**: \(.value.usage_count) times"' "$registry")

---

## Abandoned Skills (90+ days)

$(find_abandoned_skills 90 | grep -E "^  - " | sed 's/^  //')

---

## Version Health

$(check_version_health)

---

## Dependency Graph

$(generate_dependency_graph)

---

## Recommendations

EOF

  # 動態生成建議
  unused=$(jq '[.skills | to_entries[] | select(.value.usage_count == 0 or .value.usage_count == null)] | length' "$registry")
  outdated=$(jq '[.skills | to_entries[] | select(.value.sync_status == "outdated")] | length' "$registry")

  if [ "$unused" -gt 0 ]; then
    echo "- Consider removing $unused unused skills" >> "$report_file"
  fi

  if [ "$outdated" -gt 0 ]; then
    echo "- Update $outdated outdated skills" >> "$report_file"
  fi

  echo "" >> "$report_file"
  echo "✅ Report generated: $report_file"
}

# 使用範例
generate_full_report
```

### 記錄 Skill 使用

```bash
record_skill_usage() {
  local skill_name="$1"
  local agent_name="$2"
  local registry="$HOME/.claude/skills_registry.json"

  # 增加使用次數
  jq ".skills[\"$skill_name\"].usage_count += 1" "$registry" > "$registry.tmp" \
    && mv "$registry.tmp" "$registry"

  # 更新最後使用時間
  jq ".skills[\"$skill_name\"].last_used = \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"" "$registry" > "$registry.tmp" \
    && mv "$registry.tmp" "$registry"

  # 記錄使用者 agent（如果不在清單中）
  used_by=$(jq -r ".skills[\"$skill_name\"].used_by_agents // []" "$registry")
  if ! echo "$used_by" | grep -q "$agent_name"; then
    jq ".skills[\"$skill_name\"].used_by_agents += [\"$agent_name\"]" "$registry" > "$registry.tmp" \
      && mv "$registry.tmp" "$registry"
  fi
}

# 使用範例（在 agent 中呼叫）
record_skill_usage "github-api-operations" "skill-tracker"
```

## 輸出格式

### 統計摘要

```
📊 Usage Statistics Summary

Total Skills: 18
  - Upstream: 12
  - Custom: 6

Total Usage: 327 times
Average usage per skill: 18.2

Top 5 most used:
  42x - github-api-operations
  35x - json-registry-manager
  28x - version-comparison
  22x - file-classification
  18x - cross-platform-path

Unused skills: 3
```

### 健康度報告

```
🏥 Skill Health Report

✅ Healthy: 12 skills
⚠️  Outdated: 2 skills
🔴 Conflicts: 0 skills
❓ Unknown: 1 skill

Action required:
  - Update: version-comparison, file-classification
  - Review: custom-tool (unknown status)
```

## 相關規則

- `rules/usage-tracking-policy.md`：何時記錄使用、隱私考量
- `rules/report-generation-schedule.md`：報告生成頻率
- `rules/no-silent-failures.md`：統計錯誤必須記錄
