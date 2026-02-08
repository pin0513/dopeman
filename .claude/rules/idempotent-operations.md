---
name: Idempotent Operations
description: All operations must produce the same result when executed multiple times
---

# Idempotent Operations

## 適用範圍

- 適用於：所有 agents

## 規則內容

### 所有操作必須可重複執行

相同的輸入執行多次，結果應該一致：

**檔案操作（file-organizer）**：
- 移動檔案：若目標已存在且內容相同，跳過不報錯
- 刪除檔案：若已不存在，回報成功而非錯誤
- 創建目錄：若已存在，不重複創建

**資料更新（所有 agents）**：
- JSON registry 寫入：比對新舊內容，相同則跳過
- 版本記錄：檢查現有版本，避免重複記錄
- 日誌追加：使用唯一 ID 避免重複條目

**API 呼叫（skill-tracker, skill-scout）**：
- 檢查快取：相同請求優先使用快取結果
- 避免重複提交：使用冪等性 token 或檢查狀態

### 實作模式

**檢查後執行（Check-Then-Act）**：
```
IF 目標狀態已達成 THEN
    記錄「已是目標狀態，跳過」
ELSE
    執行操作
END IF
```

**使用唯一識別符**：
```json
{
  "operation_id": "20260207-223045-file-move-abc123",
  "status": "completed",
  "idempotency_key": "sha256(operation_details)"
}
```

### 驗證方式

1. **單元測試**：執行操作兩次，驗證結果一致
2. **日誌檢查**：第二次執行應有「skipped - already done」記錄
3. **資料驗證**：檢查 JSON registry 無重複條目

## 違反判定

- 違反情境 1：重複執行導致錯誤（如「檔案已存在」錯誤）
- 違反情境 2：重複執行導致資料重複（如 JSON 中出現兩筆相同記錄）
- 違反情境 3：重複執行導致狀態不一致（如計數器累加而非設定）
- 違反情境 4：無法判斷操作是否已執行（缺少狀態記錄）

## 例外情況

- 明確的「累加操作」（如統計計數）不需冪等
- 時間敏感操作（如「取得當前時間」）結果可不同
- 用戶明確要求「強制重新執行」時（需記錄原因）
