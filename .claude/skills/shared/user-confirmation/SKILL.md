---
name: User Confirmation
description: 重要操作前向使用者確認
---

# User Confirmation

## 描述

提供標準化的使用者確認機制，用於刪除檔案、覆寫資料、批次操作等高風險動作。

## 使用者

- **所有 agents**：任何可能影響現有資料的操作都應使用

## 核心知識

### 需要確認的操作

| 操作類型 | 範例 | 風險等級 |
|---------|------|---------|
| 刪除檔案 | `rm file.md` | 🔴 高 |
| 覆寫檔案 | `cp new.md old.md` | 🟡 中 |
| 批次修改 | 同步 10+ 檔案 | 🟡 中 |
| 權限變更 | `chmod 777` | 🔴 高 |
| Git 操作 | `git push --force` | 🔴 高 |

### 確認層級

1. **簡單確認**：Y/N 問題
2. **詳細確認**：顯示影響範圍後確認
3. **二次確認**：高風險操作需要輸入特定文字

## 範例

### 簡單確認

```bash
confirm() {
  local message="$1"

  echo -n "$message (y/N): "
  read -r response

  case "$response" in
    [yY]|[yY][eE][sS])
      return 0
      ;;
    *)
      echo "❌ Operation cancelled"
      return 1
      ;;
  esac
}

# 使用範例
if confirm "Delete all outdated skills?"; then
  # 執行刪除
  echo "✅ Deleted"
fi
```

### 詳細確認

```bash
confirm_with_details() {
  local message="$1"
  shift
  local details=("$@")

  echo "⚠️  $message"
  echo ""
  echo "Affected items:"
  for item in "${details[@]}"; do
    echo "  - $item"
  done
  echo ""

  echo -n "Proceed? (y/N): "
  read -r response

  case "$response" in
    [yY]|[yY][eE][sS])
      return 0
      ;;
    *)
      echo "❌ Operation cancelled"
      return 1
      ;;
  esac
}

# 使用範例
files=("skill1.md" "skill2.md" "skill3.md")
if confirm_with_details "About to delete 3 files" "${files[@]}"; then
  for file in "${files[@]}"; do
    rm "$file"
  done
fi
```

### 二次確認（高風險）

```bash
confirm_dangerous() {
  local message="$1"
  local keyword="$2"

  echo "🔴 DANGEROUS OPERATION"
  echo "$message"
  echo ""
  echo "Type '$keyword' to confirm:"
  read -r response

  if [ "$response" == "$keyword" ]; then
    return 0
  else
    echo "❌ Confirmation failed. Operation cancelled."
    return 1
  fi
}

# 使用範例
if confirm_dangerous "This will DELETE ALL custom skills permanently" "DELETE ALL"; then
  rm -rf .claude/skills/custom/*
fi
```

### 批次操作確認

```bash
confirm_batch_operation() {
  local operation="$1"
  local count="$2"
  local sample_items=("${@:3:3}")  # 顯示前 3 個範例

  echo "⚠️  Batch Operation: $operation"
  echo "Total items: $count"
  echo ""
  echo "Sample items:"
  for item in "${sample_items[@]}"; do
    echo "  - $item"
  done

  if [ "$count" -gt 3 ]; then
    echo "  ... and $((count - 3)) more"
  fi
  echo ""

  echo -n "Proceed with all $count items? (y/N): "
  read -r response

  case "$response" in
    [yY]|[yY][eE][sS])
      return 0
      ;;
    *)
      echo "❌ Operation cancelled"
      return 1
      ;;
  esac
}

# 使用範例
all_files=($(find .claude/skills -name "SKILL.md"))
count=${#all_files[@]}
sample=("${all_files[@]:0:3}")

if confirm_batch_operation "Sync all skills" "$count" "${sample[@]}"; then
  for file in "${all_files[@]}"; do
    sync_file "$file"
  done
fi
```

### 選單式確認

```bash
confirm_with_options() {
  local message="$1"

  echo "$message"
  echo ""
  echo "Options:"
  echo "  1) Yes, proceed"
  echo "  2) No, cancel"
  echo "  3) Show more details"
  echo ""
  echo -n "Your choice: "
  read -r choice

  case "$choice" in
    1)
      return 0
      ;;
    2)
      echo "❌ Operation cancelled"
      return 1
      ;;
    3)
      # 顯示更多資訊後再次詢問
      show_more_details
      confirm_with_options "$message"
      ;;
    *)
      echo "Invalid choice. Operation cancelled."
      return 1
      ;;
  esac
}
```

### 自動化模式（跳過確認）

```bash
# 環境變數控制
AUTO_CONFIRM=${AUTO_CONFIRM:-false}

confirm_or_auto() {
  local message="$1"

  if [ "$AUTO_CONFIRM" == "true" ]; then
    echo "⚡ Auto-confirmed: $message"
    return 0
  fi

  confirm "$message"
}

# 使用範例
# 手動模式
confirm_or_auto "Delete outdated skills?"

# 自動化模式（CI/CD）
AUTO_CONFIRM=true confirm_or_auto "Delete outdated skills?"
```

## 輸出格式

### 確認提示標準格式

```
⚠️  [Operation Type] [Description]

Affected items:
  - item1
  - item2
  - item3

Proceed? (y/N):
```

### 高風險提示格式

```
🔴 DANGEROUS OPERATION
[Description of danger]

This action:
  - ❌ Cannot be undone
  - ❌ Will affect X files
  - ⚠️  May break existing functionality

Type 'CONFIRM' to proceed:
```

## 相關規則

- `rules/no-silent-failures.md`：拒絕確認視為正常流程，不是錯誤
- `rules/safe-file-operations.md`：檔案操作前必須確認
- `rules/user-control.md`：重要決策必須讓使用者參與
