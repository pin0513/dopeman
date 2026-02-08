---
name: No Silent Failures
description: All errors must be explicitly logged and notified to ensure visibility of system issues
---

# No Silent Failures

## 適用範圍

- 適用於：所有 agents（coordinator, file-organizer, skill-tracker, skill-scout, usage-analyst, sync-manager）

## 規則內容

### 所有錯誤必須明確記錄與通知

任何執行失敗、異常、警告都必須：
1. 記錄到 `~/.claude/memory/dopethingsman/operation.log`
2. 包含時間戳、錯誤類型、錯誤訊息、堆疊追蹤
3. 立即通知 coordinator（透過 `SendMessage`）
4. 若為關鍵錯誤，發送 Teams 通知給用戶

### 錯誤級別分類

**CRITICAL**：系統無法繼續運作
- 範例：JSON registry 損壞、必要目錄不存在
- 動作：立即停止、通知用戶、等待修復

**ERROR**：任務失敗但不影響其他功能
- 範例：GitHub API 403、檔案移動失敗
- 動作：記錄錯誤、回報 coordinator、建議重試

**WARNING**：非預期狀況但可繼續
- 範例：找不到某個 skill 來源、快取過期
- 動作：記錄警告、繼續執行、定期檢視

### 日誌格式

```json
{
  "timestamp": "2026-02-07T22:30:45Z",
  "agent": "skill-tracker",
  "level": "ERROR",
  "message": "Failed to fetch GitHub repo metadata",
  "details": {
    "repo": "user/repo",
    "error": "403 Forbidden - Rate limit exceeded",
    "retry_after": "3600s"
  },
  "stack_trace": "..."
}
```

## 違反判定

- 違反情境 1：發生錯誤但未寫入 `operation.log`
- 違反情境 2：CRITICAL 錯誤未通知用戶
- 違反情境 3：ERROR 未回報給 coordinator
- 違反情境 4：日誌格式不完整（缺少 timestamp 或 error details）

## 例外情況

- 預期的「找不到」狀況（如掃描目錄時某些檔案不存在）可記錄為 INFO 級別，不算違反
