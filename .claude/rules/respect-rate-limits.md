---
name: Respect Rate Limits
description: GitHub API must respect rate limits to avoid service disruption
---

# Respect Rate Limits

## 適用範圍

- 適用於：skill-tracker, skill-scout
- 相關 skill：`github-api-operations`

## 規則內容

### GitHub API 必須遵守 rate limit

GitHub API 有以下限制：
- **未認證**：60 次/小時
- **已認證**：5000 次/小時（使用 Personal Access Token）
- **GraphQL API**：5000 points/小時

### 實作策略

**1. 使用認證 token**
```bash
export GITHUB_TOKEN="ghp_xxxxx"
gh api repos/{owner}/{repo} --header "Authorization: token $GITHUB_TOKEN"
```

**2. 快取機制**
- 快取 repo metadata：有效期 1 小時
- 快取 releases 列表：有效期 6 小時
- 快取 stars/forks 數：有效期 24 小時

快取位置：`~/.claude/memory/dopethingsman/github-cache.json`

**3. 批次請求**
- 收集需要檢查的 repos
- 優先檢查高優先級（用戶常用的）
- 分批執行（避免一次性耗盡 quota）

**4. 檢查剩餘 quota**
```bash
gh api rate_limit
```

回應範例：
```json
{
  "resources": {
    "core": {
      "limit": 5000,
      "remaining": 4823,
      "reset": 1709856000
    }
  }
}
```

### Rate limit 預警機制

**剩餘 > 1000**：正常使用
**剩餘 500-1000**：WARNING 警告，優先使用快取
**剩餘 < 500**：CRITICAL 嚴重，暫停非緊急請求
**剩餘 = 0**：完全停止，等待 reset 時間

### 403 錯誤處理

收到 `403 Forbidden - Rate limit exceeded` 時：
1. 記錄錯誤到 `operation.log`
2. 解析 `X-RateLimit-Reset` header（reset 時間）
3. 通知 coordinator 與用戶：「GitHub rate limit 已用盡，將於 {reset_time} 恢復」
4. 暫停所有 GitHub API 呼叫
5. 到達 reset 時間後自動恢復

### 降級方案

當 rate limit 不足時：
- 跳過非必要檢查（如 stars 數更新）
- 延後低優先級任務（如搜尋新 skills）
- 使用本地快取資料（即使過期）

## 違反判定

- 違反情境 1：未使用快取機制，重複請求相同 API
- 違反情境 2：收到 403 後仍繼續請求
- 違反情境 3：未檢查 remaining quota 就執行批次請求
- 違反情境 4：未使用認證 token（限制在 60 次/小時）

## 例外情況

- 用戶明確要求「強制刷新」時，可忽略快取（但仍需檢查 quota）
- CRITICAL 級別緊急檢查（如安全漏洞通知）可優先使用 quota
