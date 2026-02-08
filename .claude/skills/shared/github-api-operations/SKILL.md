---
name: GitHub API Operations
description: 呼叫 GitHub API 取得 repo 資訊、檔案內容、版本記錄
---

# GitHub API Operations

## 描述

提供標準化的 GitHub API 操作方法，包括取得 repository 資訊、讀取檔案內容、追蹤 commits、處理 rate limits。

## 使用者

- **skill-tracker**：取得 upstream skill 的最新 commit hash、版本資訊
- **skill-scout**：探索 upstream repo 的檔案結構、尋找新 skills

## 核心知識

### API Endpoints

```typescript
// 取得檔案內容
GET /repos/{owner}/{repo}/contents/{path}

// 取得 commit 歷史
GET /repos/{owner}/{repo}/commits?path={file_path}

// 取得特定 commit 資訊
GET /repos/{owner}/{repo}/commits/{commit_sha}

// 取得目錄樹
GET /repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1
```

### Rate Limit 處理

```bash
# 檢查剩餘額度
gh api rate_limit

# 結果範例：
# {
#   "resources": {
#     "core": {
#       "limit": 5000,
#       "remaining": 4999,
#       "reset": 1372700873
#     }
#   }
# }
```

### 錯誤處理

- **404 Not Found**：檔案或 repo 不存在
- **403 Forbidden**：超過 rate limit 或無權限
- **422 Unprocessable**：路徑格式錯誤

必須捕捉並回報清楚的錯誤訊息給使用者。

## 範例

### 取得檔案最新 commit

```bash
# 使用 gh CLI
gh api repos/OWNER/REPO/commits \
  --jq '.[0] | {sha: .sha, date: .commit.author.date, message: .commit.message}' \
  -F path="path/to/file.md"
```

### 讀取檔案內容

```bash
# Base64 解碼
gh api repos/OWNER/REPO/contents/path/to/file.md \
  --jq '.content' | base64 -d
```

### 檢查檔案是否存在

```bash
# 回傳 0 表示存在，1 表示不存在
gh api repos/OWNER/REPO/contents/path/to/file.md \
  --silent 2>/dev/null && echo "exists" || echo "not found"
```

## 相關規則

- `rules/respect-rate-limits.md`：必須檢查並遵守 GitHub API 限制
- `rules/no-silent-failures.md`：API 錯誤必須記錄並回報
