---
name: Log All Actions
description: All file operations and API calls must be logged for audit and debugging
---

# Log All Actions

## 適用範圍

- 適用於：所有 agents

## 規則內容

### 所有操作必須記錄

以下操作必須寫入 `operation.log`：

**檔案系統操作**：
- 檔案移動：`mv {source} → {destination}`
- 檔案刪除：`rm {path}` → `.trash/{timestamp}/`
- 目錄創建：`mkdir {path}`
- 備份操作：`backup {source} → .backup/{timestamp}/`

**API 呼叫**：
- GitHub API：`GET repos/{owner}/{repo}` → `200 OK` / `403 Rate Limit`
- WebSearch：`query: "{keywords}"` → `{result_count} results`
- Teams 通知：`send notification to channel {id}` → `success`

**資料更新**：
- JSON registry 寫入：`update skills-registry.json` → `+3 new, ~2 updated`
- Memory 更新：`write {key} = {value}`
- 配置變更：`set {setting} = {new_value}` (was: `{old_value}`)

### 日誌格式

```
[2026-02-07 22:30:45] [skill-tracker] [INFO] Checking updates for 15 skills
[2026-02-07 22:30:46] [skill-tracker] [API] GET github.com/user/repo/releases/latest → 200
[2026-02-07 22:30:47] [skill-tracker] [UPDATE] Found update: v1.2.3 → v1.2.4
[2026-02-07 22:30:48] [skill-tracker] [WRITE] Updated skills-registry.json (+1 update)
```

### 日誌級別

```
DEBUG   → 詳細除錯資訊（預設不記錄，除非啟用 verbose mode）
INFO    → 一般操作記錄
WARNING → 非預期但可繼續
ERROR   → 操作失敗
CRITICAL→ 系統無法繼續
```

### 日誌輪替

```
operation.log          ← 當前日誌（最新）
operation.log.1        ← 昨天（壓縮）
operation.log.2        ← 前天（壓縮）
...
operation.log.2026-02/ ← 本月歸檔（壓縮）
```

- 單檔超過 10MB：壓縮並輪替
- 保留最近 7 天完整日誌
- 7 天以上：每日壓縮歸檔
- 30 天以上：每月歸檔

### 敏感資訊保護

**禁止記錄**：
- API tokens / secrets
- 使用者密碼 / credentials
- 完整檔案內容（僅記錄路徑與 hash）

**遮蔽處理**：
```
❌ GitHub token: ghp_1234567890abcdef
✅ GitHub token: ghp_***...def (masked)
```

## 違反判定

- 違反情境 1：檔案移動但未記錄到 `operation.log`
- 違反情境 2：API 呼叫未記錄（無法追蹤 rate limit 使用量）
- 違反情境 3：日誌缺少時間戳或 agent 名稱
- 違反情境 4：敏感資訊未遮蔽直接記錄

## 例外情況

- 唯讀查詢（如 `ls`, `cat`）可選擇性記錄（避免日誌過多）
- DEBUG 級別日誌預設關閉（除非用戶啟用 `--verbose`）
- 快取命中（cache hit）可簡化記錄（僅記錄「使用快取」而非完整請求）
