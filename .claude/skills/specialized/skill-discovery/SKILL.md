---
name: Skill Discovery
description: 探索 upstream repo 中的新 skills
---

# Skill Discovery

## 描述

自動探索 upstream repositories 中的新 skills，解析 skill 資訊，建議使用者是否採用。

## 使用者

- **skill-scout**：唯一使用者，負責探索新的可用 skills

## 核心知識

### 探索來源

| Repository | 路徑模式 | 優先級 |
|-----------|---------|--------|
| anthropics/claude-code | `skills/***/SKILL.md` | 高 |
| anthropics/prompt-library | `skills/**/*.md` | 中 |
| community repos | 自訂規則 | 低 |

### Skill 識別規則

1. **檔名為 `SKILL.md`**：標準化 skill
2. **Frontmatter 包含 `name:` 和 `description:`**：有效 skill
3. **路徑包含 `skills/`**：潛在 skill

### 評估標準

| 標準 | 權重 | 評分項目 |
|------|------|---------|
| 文件完整度 | 30% | 有無範例、描述清晰度 |
| 更新頻率 | 20% | 最近一次 commit 時間 |
| 適用性 | 30% | 是否符合團隊需求 |
| 依賴性 | 20% | 是否依賴其他 skills |

## 範例

### 掃描 Upstream Repo

```bash
discover_skills_in_repo() {
  local repo="$1"
  local discovered_file="/tmp/discovered_skills.json"

  echo "🔍 Discovering skills in: $repo"
  echo ""

  # 使用 GitHub API 取得檔案樹
  tree=$(gh api "repos/$repo/git/trees/main?recursive=1" --jq '.tree')

  # 過濾出 SKILL.md 檔案
  skills=$(echo "$tree" | jq -r '.[] | select(.path | test("skills/.*SKILL\\.md$")) | .path')

  echo "Found skill files:"
  echo "$skills"
  echo ""

  # 初始化結果
  echo '{"skills": []}' > "$discovered_file"

  # 逐一解析
  for skill_path in $skills; do
    echo "Analyzing: $skill_path"

    # 讀取檔案內容
    content=$(gh api "repos/$repo/contents/$skill_path" --jq '.content' | base64 -d)

    # 解析 frontmatter
    name=$(echo "$content" | grep -E '^name:' | head -1 | sed 's/name: *//')
    description=$(echo "$content" | grep -E '^description:' | head -1 | sed 's/description: *//')

    # 取得最後 commit
    last_commit=$(gh api "repos/$repo/commits?path=$skill_path" --jq '.[0]')
    commit_sha=$(echo "$last_commit" | jq -r '.sha')
    commit_date=$(echo "$last_commit" | jq -r '.commit.author.date')

    # 評估適用性
    relevance=$(evaluate_skill_relevance "$name" "$description" "$content")

    # 加入結果
    jq ".skills += [{
      \"name\": \"$name\",
      \"description\": \"$description\",
      \"repo\": \"$repo\",
      \"path\": \"$skill_path\",
      \"last_commit\": \"$commit_sha\",
      \"last_updated\": \"$commit_date\",
      \"relevance_score\": $relevance
    }]" "$discovered_file" > "$discovered_file.tmp" \
      && mv "$discovered_file.tmp" "$discovered_file"
  done

  echo ""
  echo "✅ Discovery completed"
  echo "Results saved to: $discovered_file"
}

# 使用範例
discover_skills_in_repo "anthropics/claude-code"
```

### 評估 Skill 相關性

```bash
evaluate_skill_relevance() {
  local name="$1"
  local description="$2"
  local content="$3"
  local score=0

  # 1. 檢查是否已有類似 skill
  existing=$(jq -r ".skills | keys[]" ~/.claude/skills_registry.json 2>/dev/null)
  if echo "$existing" | grep -qi "$name"; then
    # 已存在，降低相關性
    ((score -= 20))
  fi

  # 2. 檢查關鍵字匹配（根據團隊需求）
  keywords=("github" "api" "file" "sync" "version" "registry")
  for keyword in "${keywords[@]}"; do
    if echo "$description" | grep -qi "$keyword"; then
      ((score += 10))
    fi
  done

  # 3. 檢查文件完整度
  if echo "$content" | grep -q "## 範例"; then
    ((score += 15))
  fi
  if echo "$content" | grep -q "## 使用者"; then
    ((score += 10))
  fi

  # 4. 正規化分數 (0-100)
  if [ $score -lt 0 ]; then score=0; fi
  if [ $score -gt 100 ]; then score=100; fi

  echo "$score"
}
```

### 生成發現報告

```bash
generate_discovery_report() {
  local discovered_file="$1"

  cat << 'EOF'
╔════════════════════════════════════════╗
║   Skill Discovery Report               ║
╚════════════════════════════════════════╝

EOF

  total=$(jq '.skills | length' "$discovered_file")
  high_relevance=$(jq '[.skills[] | select(.relevance_score >= 60)] | length' "$discovered_file")
  medium_relevance=$(jq '[.skills[] | select(.relevance_score >= 30 and .relevance_score < 60)] | length' "$discovered_file")

  echo "Total skills found: $total"
  echo "High relevance: $high_relevance"
  echo "Medium relevance: $medium_relevance"
  echo ""

  echo "┌─ High Relevance Skills ────────────────"
  jq -r '.skills[] | select(.relevance_score >= 60) | "│ ✨ \(.name) (score: \(.relevance_score))\n│    \(.description)\n│    Repo: \(.repo)\n│"' "$discovered_file"
  echo "└────────────────────────────────────────"
  echo ""

  echo "┌─ Medium Relevance Skills ──────────────"
  jq -r '.skills[] | select(.relevance_score >= 30 and .relevance_score < 60) | "│ 💡 \(.name) (score: \(.relevance_score))\n│    \(.description)\n│"' "$discovered_file"
  echo "└────────────────────────────────────────"
}

# 使用範例
generate_discovery_report "/tmp/discovered_skills.json"
```

### 比較 Local 與 Discovered

```bash
compare_with_local() {
  local discovered_file="$1"

  echo "📊 Comparing with local skills..."
  echo ""

  # 讀取本地 skills
  local_skills=$(jq -r '.skills | keys[]' ~/.claude/skills_registry.json)

  # 讀取發現的 skills
  discovered_skills=$(jq -r '.skills[].name' "$discovered_file")

  # 找出新 skills（不在本地）
  new_skills=()
  for skill in $discovered_skills; do
    if ! echo "$local_skills" | grep -q "^$skill$"; then
      new_skills+=("$skill")
    fi
  done

  if [ ${#new_skills[@]} -eq 0 ]; then
    echo "✅ No new skills found"
  else
    echo "🆕 New skills available:"
    for skill in "${new_skills[@]}"; do
      info=$(jq -r ".skills[] | select(.name == \"$skill\") | \"  - \(.name)\n    \(.description)\n    Score: \(.relevance_score)\"" "$discovered_file")
      echo "$info"
      echo ""
    done
  fi
}

# 使用範例
compare_with_local "/tmp/discovered_skills.json"
```

### 互動式採用流程

```bash
adopt_discovered_skill() {
  local discovered_file="$1"

  # 顯示高相關性 skills
  high_skills=$(jq -r '.skills[] | select(.relevance_score >= 60) | .name' "$discovered_file")

  if [ -z "$high_skills" ]; then
    echo "No high-relevance skills to adopt"
    return
  fi

  echo "📦 High-relevance skills available:"
  echo ""

  # 顯示清單
  IFS=$'\n' read -r -d '' -a skills_array <<< "$high_skills"
  for i in "${!skills_array[@]}"; do
    skill="${skills_array[$i]}"
    info=$(jq -r ".skills[] | select(.name == \"$skill\") | \"\(.description) (Score: \(.relevance_score))\"" "$discovered_file")
    echo "  $((i+1)). $skill"
    echo "     $info"
    echo ""
  done

  echo -n "Select skill to adopt (number, or 0 to skip): "
  read -r choice

  if [ "$choice" -eq 0 ]; then
    echo "Skipped"
    return
  fi

  selected_skill="${skills_array[$((choice-1))]}"
  skill_info=$(jq -r ".skills[] | select(.name == \"$selected_skill\")" "$discovered_file")

  repo=$(echo "$skill_info" | jq -r '.repo')
  path=$(echo "$skill_info" | jq -r '.path')

  echo ""
  echo "Adopting: $selected_skill"
  echo "From: $repo/$path"
  echo ""

  # 下載並安裝
  # （呼叫 sync-manager 或直接執行）
  echo "✅ Skill adopted successfully"
}

# 使用範例
adopt_discovered_skill "/tmp/discovered_skills.json"
```

## 輸出格式

### 發現通知

```
🔍 Skill Discovery: anthropics/claude-code

Scanning skills directory...
Found 25 SKILL.md files

Analyzing relevance...
[=========>              ] 12/25

Results:
  ✨ High relevance: 5 skills
  💡 Medium relevance: 10 skills
  📋 Low relevance: 10 skills

See full report: /tmp/discovered_skills.json
```

### 推薦清單

```
🆕 New Skills Recommended

1. ✨ github-webhook-handler (Score: 85)
   Handle GitHub webhook events
   Repo: anthropics/claude-code

2. ✨ json-schema-validator (Score: 75)
   Validate JSON against schema
   Repo: anthropics/claude-code

3. 💡 docker-compose-manager (Score: 55)
   Manage Docker Compose services
   Repo: community/devops-skills

Adopt these skills? (y/N):
```

## 相關規則

- `rules/respect-rate-limits.md`：探索時遵守 GitHub API 限制
- `rules/skill-adoption-policy.md`：決定是否採用新 skill 的標準
- `rules/no-silent-failures.md`：探索錯誤必須記錄
