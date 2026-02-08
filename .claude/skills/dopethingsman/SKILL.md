---
name: DopeThingsMan
description: 智能環境管理秘書團隊，負責 skills 管理、目錄整理、使用分析與跨電腦同步
---

# DopeThingsMan

## 功能

DopeThingsMan 是一個智能環境管理團隊，提供：
- **環境整理** - 自動分類目錄、識別專案狀態
- **Skills 生命週期管理** - 追蹤來源、檢測更新、管理繼承鏈
- **Skills 市場探索** - 發現熱門新 skills、評估品質、推薦引入
- **使用分析優化** - 統計習慣、識別冷門/過載、提供優化建議
- **跨電腦同步** - 匯出/匯入環境配置

## 使用方式

### 基本語法

```bash
/dopethingsman [command] [options]
```

### 可用命令

| 命令 | 說明 | 範例 |
|------|------|------|
| `check-updates` | 檢查 skills 更新 | `/dopethingsman check-updates` |
| `organize <path>` | 整理指定目錄 | `/dopethingsman organize ~/DEV` |
| `export-config` | 匯出環境配置 | `/dopethingsman export-config` |
| `import-config` | 匯入環境配置 | `/dopethingsman import-config` |
| `usage-report` | 產生使用報告 | `/dopethingsman usage-report --period=30days` |
| `discover-skills` | 搜尋推薦的新 skills | `/dopethingsman discover-skills` |
| `health-check` | 完整環境健檢 | `/dopethingsman health-check` |
| `control-center` (別名: `cc`) | 開啟 Skills 總控台 Dashboard | `/dopethingsman cc` |
| `stop-dashboard` (別名: `scc`) | 停止 Dashboard 伺服器 | `/dopethingsman scc` |

### 自動啟動模式

啟動 DopeThingsMan 時自動執行：
- 掃描目錄結構
- 檢查 skills 更新
- 搜尋新推薦
- 分析使用數據

## 範例

### 檢查更新

```bash
/dopethingsman check-updates
```

輸出：
```
🔍 檢查 skills 更新...

✓ 已檢查 12 個 skills
⚠️ 發現 2 個可更新：
  - version-comparison: v1.1.0 → v1.2.0
  - file-classification: v2.0.0 → v2.1.0

執行 "sync upstream" 來更新這些 skills。
```

### 整理目錄

```bash
/dopethingsman organize ~/DEV
```

輸出：
```
📂 掃描 ~/DEV...

已分類：
  📁 產出區：3 個專案
  📁 工作區：5 個專案
  📁 參考區：2 個 repos
  📁 暫存區：1 個 demo

建議：
  - demo/old-test 已 90 天未修改，建議歸檔
```

### 使用報告

```bash
/dopethingsman usage-report --period=30days
```

輸出：
```
📊 使用統計（最近 30 天）

Skills 使用頻率：
  1. github-api-operations: 42 次
  2. dev-team-pm: 28 次
  3. slide-export: 15 次
  ...

優化建議：
  ⚠️ old-skill-1 已 180 天未使用，建議移除
  💡 考慮安裝 playwright-helper（可節省 60% E2E 測試時間）
```

### Control Center

```bash
/dopethingsman control-center
```

自動執行：
1. 掃描全域 Skills、專案 Skills、開發中 Skills
2. 掃描全域 Rules、專案 Rules
3. 掃描所有 Agents (Coordinators & Workers)
4. 掃描所有 Commands
5. 建立分層架構視圖
6. 啟動 HTTP 伺服器（端口 8891）
7. 開啟瀏覽器到 Dashboard

輸出：
```
🎛️  DopeThingsMan - Control Center Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 啟動 HTTP 伺服器...
   目錄: ~/DEV/projects/dopethingsman/commands
   端口: 8891

✅ 伺服器已啟動 (PID: 12345)

📍 Dashboard URL: http://localhost:8891/control-center-real.html
📋 日誌位置: /tmp/dopethingsman-dashboard.log
🔧 PID 檔案: /tmp/dopethingsman-dashboard.pid

✅ 已開啟瀏覽器

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 提示：
   - 伺服器將持續運行在背景
   - 關閉瀏覽器不會停止伺服器
   - 使用 /dopethingsman scc 停止伺服器
```

### 停止 Dashboard

```bash
/dopethingsman stop-dashboard
```

輸出：
```
🛑 停止 DopeThingsMan Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

正在停止伺服器 (PID: 12345)...
✅ 伺服器已停止

📋 日誌位置: /tmp/dopethingsman-dashboard.log
```

## 技術細節

### 團隊架構

DopeThingsMan 使用 **Subagent 模式**：
- `dopethingsman-coordinator` - 總調度者
- `file-organizer` - 目錄整理專家
- `skill-tracker` - Skills 更新追蹤
- `skill-scout` - Skills 市場探索
- `usage-analyst` - 使用分析師
- `sync-manager` - 同步管理員

### 資料位置

```
~/.claude/memory/dopethingsman/
├── skills-registry.json         ← Skill 來源與版本記錄
├── skill-recommendations.json   ← 推薦的新 skills
├── usage-report.json            ← 使用統計報告
├── operation.log                ← 操作日誌
└── github-cache.json            ← GitHub API 快取
```

### 專案位置

```
~/DEV/projects/dopethingsman/
├── CLAUDE.md
└── .claude/
    ├── agents/
    ├── skills/
    └── rules/
```

## 注意事項

1. **GitHub API Rate Limit**：使用快取機制避免超過限制
2. **備份機制**：所有修改操作前自動備份
3. **冪等性**：所有操作可重複執行
4. **日誌記錄**：所有操作記錄到 `operation.log`
5. **無靜默失敗**：所有錯誤必須明確通知

## 相關資源

- **專案文件**: `~/DEV/projects/dopethingsman/CLAUDE.md`
- **操作日誌**: `~/.claude/memory/dopethingsman/operation.log`
- **Registry**: `~/.claude/memory/dopethingsman/skills-registry.json`

---

**版本**: v1.0.0
**專案位置**: `/Users/paul_huang/DEV/projects/dopethingsman`
