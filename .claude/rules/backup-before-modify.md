---
name: Backup Before Modify
description: All data modifications must be preceded by a backup to prevent data loss
---

# Backup Before Modify

## 適用範圍

- 適用於：所有 agents
- 重點適用：file-organizer, sync-manager, coordinator

## 規則內容

### 修改資料前必須備份

在執行以下操作前，必須先建立備份：
1. **檔案移動/刪除**：備份到 `.backup/{timestamp}/`
2. **JSON registry 更新**：保留舊版為 `{filename}.backup.json`
3. **配置檔修改**：保留舊版為 `{filename}.{timestamp}.bak`
4. **批次操作**：整體備份後再執行

### 備份策略

**即時備份**（操作前立即執行）：
- 檔案刪除/移動
- JSON registry 寫入
- 環境配置匯入

**定期備份**（每日自動執行）：
- 完整 memory 目錄快照
- Skills registry 快照
- Operation logs 歸檔

### 備份保留策略

```
.backup/
├── 2026-02-07_22-30-45/    ← 最近 7 天：完整保留
├── 2026-02-01/              ← 7-30 天：每日一份
└── 2026-01/                 ← 30 天以上：每月一份（壓縮）
```

### 備份驗證

- 備份完成後必須驗證檔案完整性（checksum）
- 記錄備份位置到 `backup-index.json`
- 定期測試還原流程（每月一次）

## 違反判定

- 違反情境 1：檔案移動/刪除前未建立備份
- 違反情境 2：JSON registry 更新後找不到舊版
- 違反情境 3：`.backup/` 目錄不存在或為空
- 違反情境 4：備份檔案損壞無法還原

## 例外情況

- 操作暫存目錄（`/tmp/`, `*.tmp`）可不備份
- 唯讀操作（讀取、掃描）無需備份
- 用戶明確指定 `--no-backup` 選項時（需記錄到日誌）
