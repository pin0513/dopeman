---
name: File System Operations
description: 安全的檔案與目錄操作（移動、複製、刪除）
---

# File System Operations

## 描述

提供安全的檔案系統操作，包括備份、驗證、rollback 機制，確保檔案操作不會遺失資料。

## 使用者

- **file-organizer**：唯一使用者，負責整理 .claude 目錄結構

## 核心知識

### 安全操作原則

1. **操作前備份**：移動或刪除前先備份
2. **驗證後確認**：操作後驗證目標狀態
3. **提供 rollback**：失敗時能還原
4. **記錄所有變更**：用於稽核與除錯

### 操作類型

| 操作 | 風險 | 備份策略 |
|------|------|---------|
| 移動檔案 | 中 | 保留原路徑記錄 |
| 複製檔案 | 低 | 不需備份 |
| 刪除檔案 | 高 | 移至 .trash 目錄 |
| 重新命名 | 中 | 保留舊檔名記錄 |
| 批次操作 | 高 | 完整備份或交易式操作 |

## 範例

### 安全移動檔案

```bash
safe_move() {
  local source="$1"
  local dest="$2"
  local backup_dir="$HOME/.claude/.backup/$(date +%Y%m%d-%H%M%S)"

  # 1. 驗證來源檔案存在
  if [ ! -f "$source" ]; then
    echo "❌ Source file not found: $source"
    return 1
  fi

  # 2. 確保目標目錄存在
  dest_dir=$(dirname "$dest")
  mkdir -p "$dest_dir"

  # 3. 備份（如果目標已存在）
  if [ -f "$dest" ]; then
    mkdir -p "$backup_dir"
    cp "$dest" "$backup_dir/$(basename "$dest")"
    echo "📦 Backed up existing file to: $backup_dir"
  fi

  # 4. 執行移動
  if mv "$source" "$dest"; then
    echo "✅ Moved: $source → $dest"

    # 5. 記錄操作
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|MOVE|$source|$dest" >> ~/.claude/.file_operations.log
    return 0
  else
    echo "❌ Failed to move file"
    return 1
  fi
}

# 使用範例
safe_move "/Users/paul_huang/.claude/test-agent.md" \
          "/Users/paul_huang/.claude/agents/environment/test-agent.md"
```

### 安全刪除（移至垃圾桶）

```bash
safe_delete() {
  local file="$1"
  local trash_dir="$HOME/.claude/.trash/$(date +%Y%m%d)"

  # 1. 驗證檔案存在
  if [ ! -f "$file" ]; then
    echo "❌ File not found: $file"
    return 1
  fi

  # 2. 建立垃圾桶目錄
  mkdir -p "$trash_dir"

  # 3. 移至垃圾桶（保留原始路徑資訊）
  filename=$(basename "$file")
  timestamp=$(date +%H%M%S)
  trash_file="$trash_dir/${filename}.${timestamp}"

  if mv "$file" "$trash_file"; then
    echo "🗑️  Moved to trash: $trash_file"

    # 4. 記錄原始路徑（用於還原）
    echo "$trash_file|$file" >> "$trash_dir/.trash_index"

    # 5. 記錄操作
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)|DELETE|$file|$trash_file" >> ~/.claude/.file_operations.log
    return 0
  else
    echo "❌ Failed to delete file"
    return 1
  fi
}

# 使用範例
safe_delete "/Users/paul_huang/.claude/old-agent.md"
```

### 還原刪除的檔案

```bash
restore_from_trash() {
  local trash_file="$1"
  local trash_dir=$(dirname "$trash_file")
  local index_file="$trash_dir/.trash_index"

  # 1. 查找原始路徑
  if [ ! -f "$index_file" ]; then
    echo "❌ Trash index not found"
    return 1
  fi

  original_path=$(grep "^$trash_file|" "$index_file" | cut -d'|' -f2)

  if [ -z "$original_path" ]; then
    echo "❌ Original path not found in trash index"
    return 1
  fi

  # 2. 還原檔案
  if mv "$trash_file" "$original_path"; then
    echo "✅ Restored: $original_path"

    # 3. 更新索引
    grep -v "^$trash_file|" "$index_file" > "$index_file.tmp"
    mv "$index_file.tmp" "$index_file"

    return 0
  else
    echo "❌ Failed to restore file"
    return 1
  fi
}
```

### 批次操作（交易式）

```bash
batch_move() {
  local -a operations=("$@")
  local backup_dir="$HOME/.claude/.backup/batch-$(date +%Y%m%d-%H%M%S)"
  local rollback_log="$backup_dir/rollback.sh"

  mkdir -p "$backup_dir"

  echo "#!/bin/bash" > "$rollback_log"
  echo "# Rollback script for batch operation" >> "$rollback_log"
  echo "# Generated: $(date)" >> "$rollback_log"
  echo "" >> "$rollback_log"

  # 執行所有操作
  local success=0
  local total=${#operations[@]}

  for op in "${operations[@]}"; do
    IFS='|' read -r source dest <<< "$op"

    # 備份目標檔案（如果存在）
    if [ -f "$dest" ]; then
      cp "$dest" "$backup_dir/$(basename "$dest")"
      echo "mv \"$dest\" \"$backup_dir/$(basename "$dest")\"" >> "$rollback_log"
    fi

    # 執行移動
    if mv "$source" "$dest" 2>/dev/null; then
      ((success++))
      # 記錄 rollback 指令
      echo "mv \"$dest\" \"$source\"" >> "$rollback_log"
    else
      echo "❌ Failed: $source → $dest"
      break
    fi
  done

  chmod +x "$rollback_log"

  if [ "$success" -eq "$total" ]; then
    echo "✅ Batch operation completed: $success/$total"
    return 0
  else
    echo "❌ Batch operation failed: $success/$total"
    echo "Rollback script available: $rollback_log"
    return 1
  fi
}

# 使用範例
batch_move \
  "/path/to/file1.md|/new/path/file1.md" \
  "/path/to/file2.md|/new/path/file2.md"
```

### 目錄結構比對

```bash
compare_directory_structure() {
  local dir1="$1"
  local dir2="$2"

  echo "📊 Comparing directory structures..."
  echo ""

  # 列出所有檔案（相對路徑）
  (cd "$dir1" && find . -type f | sort) > /tmp/dir1.txt
  (cd "$dir2" && find . -type f | sort) > /tmp/dir2.txt

  # 找出差異
  echo "Files only in $dir1:"
  comm -23 /tmp/dir1.txt /tmp/dir2.txt

  echo ""
  echo "Files only in $dir2:"
  comm -13 /tmp/dir1.txt /tmp/dir2.txt

  echo ""
  echo "Common files:"
  comm -12 /tmp/dir1.txt /tmp/dir2.txt | wc -l

  rm /tmp/dir1.txt /tmp/dir2.txt
}
```

### 清理垃圾桶

```bash
cleanup_trash() {
  local days_old="${1:-30}"  # 預設保留 30 天
  local trash_base="$HOME/.claude/.trash"

  echo "🗑️  Cleaning trash older than $days_old days..."

  # 找出舊目錄
  find "$trash_base" -type d -name "20*" -mtime +$days_old | while read dir; do
    echo "Removing: $dir"
    rm -rf "$dir"
  done

  echo "✅ Trash cleanup completed"
}

# 使用範例
cleanup_trash 30  # 刪除 30 天前的垃圾
```

## 操作日誌

### 日誌格式

```
2026-02-08T10:30:00Z|MOVE|/old/path/file.md|/new/path/file.md
2026-02-08T10:31:15Z|DELETE|/old/path/old-file.md|.trash/20260208/old-file.md.103115
2026-02-08T10:32:00Z|COPY|/source/file.md|/dest/file.md
```

### 查詢日誌

```bash
# 今天的所有操作
grep "^$(date +%Y-%m-%d)" ~/.claude/.file_operations.log

# 特定檔案的操作歷史
grep "/path/to/file.md" ~/.claude/.file_operations.log

# 所有刪除操作
grep "|DELETE|" ~/.claude/.file_operations.log
```

## 相關規則

- `rules/safe-file-operations.md`：檔案操作前驗證、操作後確認
- `rules/backup-before-modify.md`：修改前備份策略
- `rules/no-silent-failures.md`：檔案操作失敗必須記錄
- `rules/absolute-paths-only.md`：使用絕對路徑避免錯誤
