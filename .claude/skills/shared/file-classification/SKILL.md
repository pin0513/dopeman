---
name: File Classification
description: 判斷檔案類型並歸類到正確目錄
---

# File Classification

## 描述

根據檔案路徑、內容、frontmatter 自動判斷檔案類型（Agent、Skill、Rule、Memory 等），用於自動整理與同步。

## 使用者

- **file-organizer**：決定檔案應放置的目標目錄
- **sync-manager**：判斷檔案是否為可同步類型

## 核心知識

### 檔案類型定義

| 類型 | 識別特徵 | 標準路徑 |
|------|---------|---------|
| **Agent** | frontmatter 包含 `model:` | `.claude/agents/{category}/{name}.md` |
| **Skill** | 檔名為 `SKILL.md` | `.claude/skills/{type}/{name}/SKILL.md` |
| **Rule** | 檔名為 `*.md` 且在 rules 目錄 | `.claude/rules/{name}.md` |
| **Memory** | 檔名為 `MEMORY.md` 或 `CHANGELOG.md` | `.claude/{name}.md` |
| **Registry** | 檔名為 `skills_registry.json` | `.claude/skills_registry.json` |

### 分類邏輯

```bash
classify_file() {
  local filepath="$1"
  local filename=$(basename "$filepath")
  local dirname=$(dirname "$filepath")

  # 1. 根據檔名
  if [[ "$filename" == "SKILL.md" ]]; then
    echo "skill"
    return
  fi

  if [[ "$filename" == "MEMORY.md" ]] || [[ "$filename" == "CHANGELOG.md" ]]; then
    echo "memory"
    return
  fi

  if [[ "$filename" == "skills_registry.json" ]]; then
    echo "registry"
    return
  fi

  # 2. 根據目錄路徑
  if [[ "$dirname" == *"/.claude/agents"* ]]; then
    echo "agent"
    return
  fi

  if [[ "$dirname" == *"/.claude/rules"* ]]; then
    echo "rule"
    return
  fi

  # 3. 根據 frontmatter
  if grep -q "^model:" "$filepath" 2>/dev/null; then
    echo "agent"
    return
  fi

  # 4. 無法分類
  echo "unknown"
}
```

### Skill 子分類

```bash
classify_skill_type() {
  local skill_path="$1"

  if [[ "$skill_path" == *"/skills/shared/"* ]]; then
    echo "shared"
  elif [[ "$skill_path" == *"/skills/specialized/"* ]]; then
    echo "specialized"
  elif [[ "$skill_path" == *"/skills/custom/"* ]]; then
    echo "custom"
  else
    echo "unknown"
  fi
}
```

### Agent 子分類

```bash
classify_agent_category() {
  local agent_path="$1"

  if [[ "$agent_path" == *"/agents/environment/"* ]]; then
    echo "environment"
  elif [[ "$agent_path" == *"/agents/skills-management/"* ]]; then
    echo "skills-management"
  elif [[ "$agent_path" == *"/agents/analytics/"* ]]; then
    echo "analytics"
  else
    # 根目錄的 coordinator
    echo "root"
  fi
}
```

## 範例

### 分類單一檔案

```bash
file="/Users/paul_huang/.claude/agents/environment/file-organizer.md"
type=$(classify_file "$file")
echo "Type: $type"

if [ "$type" == "agent" ]; then
  category=$(classify_agent_category "$file")
  echo "Category: $category"
fi
```

### 批次分類目錄

```bash
# 掃描所有 .md 檔案並分類
find .claude -name "*.md" | while read file; do
  type=$(classify_file "$file")
  echo "$file -> $type"
done
```

### 驗證檔案位置正確性

```bash
check_file_location() {
  local file="$1"
  local type=$(classify_file "$file")

  case "$type" in
    agent)
      if [[ "$file" != *"/.claude/agents/"* ]]; then
        echo "❌ Agent file in wrong location: $file"
        return 1
      fi
      ;;
    skill)
      if [[ "$file" != *"/.claude/skills/"* ]]; then
        echo "❌ Skill file in wrong location: $file"
        return 1
      fi
      ;;
    rule)
      if [[ "$file" != *"/.claude/rules/"* ]]; then
        echo "❌ Rule file in wrong location: $file"
        return 1
      fi
      ;;
  esac

  echo "✅ File in correct location: $file"
  return 0
}
```

## 輸出格式

### 分類報告

```
[file-organizer] Classification Report

📁 Total files scanned: 25

📊 By Type:
  - Agents: 6
  - Skills: 12 (6 shared, 6 specialized)
  - Rules: 5
  - Memory: 2

⚠️  Issues:
  - Wrong location: 1 file
  - Unclassified: 0 files

✅ All classified files in correct locations
```

## 相關規則

- `rules/file-naming-conventions.md`：標準化檔案命名
- `rules/directory-structure.md`：標準化目錄結構
- `rules/no-silent-failures.md`：無法分類的檔案必須記錄
