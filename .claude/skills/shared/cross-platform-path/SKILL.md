---
name: Cross-Platform Path
description: 處理跨平台路徑轉換與驗證
---

# Cross-Platform Path

## 描述

提供跨平台（macOS、Linux、Windows）的路徑處理工具，確保路徑格式正確、空格處理、相對路徑轉絕對路徑。

## 使用者

- **file-organizer**：處理檔案移動時的路徑轉換
- **sync-manager**：處理不同環境間的路徑對應

## 核心知識

### 平台差異

| 平台 | 路徑分隔符 | Home 目錄 | 範例 |
|------|-----------|----------|------|
| macOS/Linux | `/` | `~` = `/Users/username` | `/Users/paul_huang/.claude` |
| Windows | `\` 或 `/` | `%USERPROFILE%` | `C:\Users\paul_huang\.claude` |

### 常見問題

1. **空格路徑**：`/Users/paul huang/` 需要引號或跳脫
2. **相對路徑**：`.claude/agents` 依賴當前工作目錄
3. **Tilde 展開**：`~/.claude` 在某些情境下不會自動展開
4. **大小寫敏感**：macOS 預設不敏感，Linux 敏感

## 範例

### 路徑正規化

```bash
normalize_path() {
  local path="$1"

  # 1. 展開 tilde
  path="${path/#\~/$HOME}"

  # 2. 移除結尾斜線
  path="${path%/}"

  # 3. 轉換為絕對路徑
  if [[ "$path" != /* ]]; then
    path="$(pwd)/$path"
  fi

  # 4. 解析 . 和 ..
  path=$(realpath "$path" 2>/dev/null || echo "$path")

  echo "$path"
}

# 使用範例
normalize_path "~/.claude/agents"
# 輸出: /Users/paul_huang/.claude/agents

normalize_path "../skills/shared"
# 輸出: /Users/paul_huang/.claude/skills/shared
```

### 安全路徑引號

```bash
safe_path() {
  local path="$1"

  # 檢查是否包含空格或特殊字元
  if [[ "$path" =~ [[:space:]] ]] || [[ "$path" =~ [\(\)\&\|] ]]; then
    echo "\"$path\""
  else
    echo "$path"
  fi
}

# 使用範例
path="/Users/paul huang/.claude/agents"
safe_path "$path"
# 輸出: "/Users/paul huang/.claude/agents"
```

### 相對路徑計算

```bash
relative_path() {
  local from="$1"
  local to="$2"

  # 使用 Python 計算相對路徑（跨平台）
  python3 -c "import os.path; print(os.path.relpath('$to', '$from'))"
}

# 使用範例
from="/Users/paul_huang/.claude/agents"
to="/Users/paul_huang/.claude/skills/shared"
relative_path "$from" "$to"
# 輸出: ../skills/shared
```

### 平台偵測

```bash
detect_platform() {
  case "$(uname -s)" in
    Darwin*)  echo "macos" ;;
    Linux*)   echo "linux" ;;
    CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
    *)        echo "unknown" ;;
  esac
}

# 使用範例
platform=$(detect_platform)
if [ "$platform" == "windows" ]; then
  # Windows 特殊處理
  path=$(cygpath -u "$path")
fi
```

### 路徑驗證

```bash
validate_path() {
  local path="$1"
  local type="$2"  # file 或 directory

  # 1. 正規化路徑
  path=$(normalize_path "$path")

  # 2. 檢查是否存在
  if [ "$type" == "file" ]; then
    if [ ! -f "$path" ]; then
      echo "❌ File not found: $path"
      return 1
    fi
  elif [ "$type" == "directory" ]; then
    if [ ! -d "$path" ]; then
      echo "❌ Directory not found: $path"
      return 1
    fi
  fi

  # 3. 檢查權限
  if [ ! -r "$path" ]; then
    echo "❌ No read permission: $path"
    return 1
  fi

  echo "✅ Valid path: $path"
  return 0
}
```

### 建立目錄（遞迴且安全）

```bash
ensure_directory() {
  local dir="$1"

  dir=$(normalize_path "$dir")

  if [ -d "$dir" ]; then
    return 0
  fi

  # 使用 -p 建立父目錄
  if mkdir -p "$dir" 2>/dev/null; then
    echo "✅ Created directory: $dir"
    return 0
  else
    echo "❌ Failed to create directory: $dir"
    return 1
  fi
}
```

## 常見錯誤處理

### 錯誤 1: 空格路徑未引號

```bash
# ❌ 錯誤
cp /Users/paul huang/.claude/agents/test.md /tmp/

# ✅ 正確
cp "/Users/paul huang/.claude/agents/test.md" /tmp/

# ✅ 更好（使用變數）
source="/Users/paul huang/.claude/agents/test.md"
dest="/tmp/"
cp "$source" "$dest"
```

### 錯誤 2: Tilde 未展開

```bash
# ❌ 錯誤（在雙引號中不會展開）
path="~/.claude"
cd "$path"  # 會失敗

# ✅ 正確
path="$HOME/.claude"
cd "$path"

# ✅ 或使用函數
path=$(normalize_path "~/.claude")
cd "$path"
```

### 錯誤 3: 相對路徑依賴

```bash
# ❌ 錯誤（相對路徑在不同工作目錄下會失敗）
cd /tmp
cat .claude/agents/test.md  # 會找不到

# ✅ 正確（使用絕對路徑）
agent_path="/Users/paul_huang/.claude/agents/test.md"
cat "$agent_path"
```

## 工具函數庫

```bash
# path_utils.sh - 可被其他 agents 引用

normalize_path() { ... }
safe_path() { ... }
relative_path() { ... }
validate_path() { ... }
ensure_directory() { ... }
detect_platform() { ... }

# 使用方式
source ~/.claude/skills/shared/cross-platform-path/path_utils.sh
path=$(normalize_path "~/teams/dopethingsman/.claude")
```

## 相關規則

- `rules/absolute-paths-only.md`：優先使用絕對路徑
- `rules/no-silent-failures.md`：路徑錯誤必須記錄
- `rules/safe-file-operations.md`：檔案操作前驗證路徑
