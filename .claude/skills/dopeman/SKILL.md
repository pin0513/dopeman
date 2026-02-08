---
name: DopeMAN
description: 智能環境管理秘書團隊，負責 skills 管理、目錄整理、使用分析與跨電腦同步
---

# DopeMAN

## 功能

DopeMAN 是一個智能環境管理團隊，提供：
- **環境整理** - 自動分類目錄、識別專案狀態
- **Skills 生命週期管理** - 追蹤來源、檢測更新、管理繼承鏈
- **Skills 市場探索** - 發現熱門新 skills、評估品質、推薦引入
- **使用分析優化** - 統計習慣、識別冷門/過載、提供優化建議
- **跨電腦同步** - 匯出/匯入環境配置

## 使用方式

### 基本語法

```bash
/dopeman [command] [options]
```

### 可用命令

| 命令 | 說明 | 範例 |
|------|------|------|
| `check-updates` | 檢查 skills 更新 | `/dopeman check-updates` |
| `install-official` | 安裝官方 Skills/Teams | `/dopeman install-official` |
| `organize <path>` | 整理指定目錄 | `/dopeman organize ~/DEV` |
| `export-config` | 匯出環境配置 | `/dopeman export-config` |
| `import-config` | 匯入環境配置 | `/dopeman import-config` |
| `usage-report` | 產生使用報告 | `/dopeman usage-report --period=30days` |
| `discover-skills` | 搜尋推薦的新 skills | `/dopeman discover-skills` |
| `health-check` | 完整環境健檢 | `/dopeman health-check` |
| `control-center` (別名: `cc`) | 開啟 Skills 總控台 Dashboard | `/dopeman cc` |
| `stop-dashboard` (別名: `scc`) | 停止 Dashboard 伺服器 | `/dopeman scc` |

### 自動啟動模式

啟動 DopeMAN 時自動執行：
- 掃描目錄結構
- 檢查 skills 更新
- 搜尋新推薦
- 分析使用數據

## 範例

### 檢查更新

```bash
/dopeman check-updates
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
/dopeman organize ~/DEV
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
/dopeman usage-report --period=30days
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

### 安裝官方 Skills/Teams

```bash
/dopeman install-official
```

自動執行：
1. 讀取官方 Skills/Teams 目錄
2. 顯示分類（官方專案、專業級 Skills、工具性 Skills、專業團隊）
3. 互動式選單讓用戶選擇安裝項目
4. 自動 clone 倉庫到適當位置
5. 建立全域連結（若為 global_link 類型）
6. 建立 commands 連結（若存在）
7. 更新 skills-registry.json

輸出：
```
============================================================
🎯 DopeMAN - 官方 Skills/Teams 管理器
============================================================

主選單：

1) 顯示官方目錄
2) 安裝 Skills/Teams
3) 檢查更新
4) 查看已安裝清單
0) 結束

請選擇 (0-4): 1

============================================================
官方 Skills / Teams 目錄
============================================================

📦 官方專案
   DopeMAN 官方維護的核心專案

   1. [未安裝] DopeMAN
      📝 智能環境管理秘書團隊
      🔗 https://github.com/pin0513/dopeman
      📂 類型: skill | 安裝方式: global_link

   2. [未安裝] CLAUDE-PUNK
      📝 Claude 客製化開發框架
      🔗 https://github.com/chemistrywow31/CLAUDE-PUNK
      📂 類型: team | 安裝方式: project

📦 專業級 Skills
   高品質、可直接使用的專業技能

   1. [未安裝] 商業教練
      📝 軟體產品策略教練
      🔗 https://github.com/pin0513/product-strategy-coach
      📂 類型: skill | 安裝方式: global_link

   2. [已安裝] 文案專家
      📝 完整文章撰寫團隊
      🔗 https://github.com/pin0513/ArticleWorld
      📂 類型: team | 安裝方式: global_link
      🏷️  版本: a3f2c1b

...

主選單：

1) 顯示官方目錄
2) 安裝 Skills/Teams
3) 檢查更新
4) 查看已安裝清單
0) 結束

請選擇 (0-4): 2

============================================================
安裝官方 Skills / Teams
============================================================

選擇安裝方式：

1) 依類別選擇
2) 全部安裝
3) 個別選擇
0) 取消

請選擇 (0-3): 1

選擇要安裝的類別：

1) 官方專案 (0/3 已安裝)
   DopeMAN 官方維護的核心專案
2) 專業級 Skills (1/5 已安裝)
   高品質、可直接使用的專業技能
3) 工具性 Skills (0/2 已安裝)
   實用工具與整合
4) 專業團隊 (0/2 已安裝)
   完整的多 Agent 團隊
0) 取消

請選擇類別 (0-4): 2

安裝 專業級 Skills 中的所有項目

ℹ️  安裝 商業教練 到 /Users/paul_huang/.claude/skills/product-strategy-coach...
ℹ️  正在 clone https://github.com/pin0513/product-strategy-coach...
✅ Clone 完成
ℹ️  建立 commands 連結: /Users/paul_huang/.claude/commands/product-strategy-coach
ℹ️  Registry 已新增: product-strategy-coach
✅ ✨ 商業教練 安裝完成！

⚠️  文案專家 已安裝，跳過

ℹ️  安裝 投影片專家 到 /Users/paul_huang/.claude/skills/slides-world...
ℹ️  正在 clone https://github.com/pin0513/SlidesWorld...
✅ Clone 完成
ℹ️  Registry 已新增: slides-world
✅ ✨ 投影片專家 安裝完成！

...
```

### Control Center

```bash
/dopeman control-center
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
🎛️  DopeMAN - Control Center Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 啟動 HTTP 伺服器...
   目錄: ~/DEV/projects/dopeman/commands
   端口: 8891

✅ 伺服器已啟動 (PID: 12345)

📍 Dashboard URL: http://localhost:8891/control-center-real.html
📋 日誌位置: /tmp/dopeman-dashboard.log
🔧 PID 檔案: /tmp/dopeman-dashboard.pid

✅ 已開啟瀏覽器

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 提示：
   - 伺服器將持續運行在背景
   - 關閉瀏覽器不會停止伺服器
   - 使用 /dopeman scc 停止伺服器
```

### 停止 Dashboard

```bash
/dopeman stop-dashboard
```

輸出：
```
🛑 停止 DopeMAN Dashboard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

正在停止伺服器 (PID: 12345)...
✅ 伺服器已停止

📋 日誌位置: /tmp/dopeman-dashboard.log
```

## 技術細節

### 團隊架構

DopeMAN 使用 **Subagent 模式**：
- `dopeman-coordinator` - 總調度者
- `file-organizer` - 目錄整理專家
- `skill-tracker` - Skills 更新追蹤
- `skill-scout` - Skills 市場探索
- `usage-analyst` - 使用分析師
- `sync-manager` - 同步管理員

### 資料位置

```
~/.claude/memory/dopeman/
├── skills-registry.json         ← Skill 來源與版本記錄
├── skill-recommendations.json   ← 推薦的新 skills
├── usage-report.json            ← 使用統計報告
├── operation.log                ← 操作日誌
└── github-cache.json            ← GitHub API 快取
```

### 專案位置

```
~/DEV/projects/dopeman/
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

- **專案文件**: `~/DEV/projects/dopeman/CLAUDE.md`
- **操作日誌**: `~/.claude/memory/dopeman/operation.log`
- **Registry**: `~/.claude/memory/dopeman/skills-registry.json`

---

**版本**: v1.0.0
**專案位置**: `/Users/paul_huang/DEV/projects/dopeman`
