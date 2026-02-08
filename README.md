# DopeMAN 🎛️

**Dev**elopment **O**rganization & **P**roject **E**nvironment **MAN**ager

智能環境管理秘書團隊，負責 Claude Code skills 生命週期管理、開發專案組織、使用分析與跨電腦同步。

[![GitHub](https://img.shields.io/badge/github-pin0513%2Fdopeman-blue)](https://github.com/pin0513/dopeman)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-purple)](https://claude.ai/code)

---

## 📋 目錄

- [核心功能](#核心功能)
- [快速開始](#快速開始)
- [Dashboard 總控台](#dashboard-總控台)
- [專案架構](#專案架構)
- [雙版本架構](#雙版本架構)
- [開發指南](#開發指南)
- [命令參考](#命令參考)

---

## 🎯 核心功能

### 1. **Skills 生命週期管理**
- 📦 **自動追蹤來源**：記錄每個 skill 的 GitHub 來源與版本
- 🔔 **更新通知**：檢測 upstream 更新，提醒用戶升級
- 🌳 **繼承鏈管理**：追蹤 forked skills 與客製化版本的關係
- 🔍 **重複偵測**：識別全域與專案中的重複 skills

### 2. **開發專案組織**
- 📂 **自動分類**：將專案分為工作、自有開發、GitHub 參考、其他下載
- 💻 **技術棧偵測**：自動識別 .NET/C#、React、Next.js、Python、Go 等
- 🤖 **Claude Team 識別**：標記包含 AI agent 團隊的專案
- 🔀 **Git 狀態追蹤**：監控未提交變更與最後 commit 資訊

### 3. **使用分析與優化**
- 📊 **使用統計**：追蹤每個 skill 的使用頻率與最後使用時間
- 💡 **智能建議**：
  - 移除建議：超過 180 天未使用的 skills
  - 拆分建議：職責過多的 agents
  - 合併建議：功能重疊的 skills
- ⚠️ **過載檢測**：識別執行時間過長的 agents

### 4. **跨電腦同步**
- 📤 **配置匯出**：打包 skills、agents、rules、使用歷史
- 📥 **配置匯入**：自動安裝缺失的 skills、恢復目錄分類規則
- 🔄 **衝突處理**：智能比對差異、提供衝突解決建議
- 💾 **自動備份**：匯入前自動備份現有配置

### 5. **Skills Market 探索**
- 🔍 **發現新 Skills**：從 GitHub 搜尋熱門的 Claude Code skills
- ⭐ **品質評分**：基於 stars、活躍度、文件、測試、社群互動評分
- 🎯 **智能推薦**：根據使用習慣推薦相關 skills
- 📈 **趨勢分析**：追蹤 skills 生態系的發展趨勢

---

## 🚀 快速開始

### 安裝

#### 方式 1：從全域 Skill 安裝（推薦）

```bash
# 1. 下載 SKILL.md 到全域 skills 目錄
curl -o ~/.claude/skills/dopeman/SKILL.md \
  https://raw.githubusercontent.com/pin0513/dopeman/main/.claude/skills/dopeman/SKILL.md

# 2. 在任何目錄呼叫
/dopeman cc
```

#### 方式 2：Clone 完整專案（開發者）

```bash
# 1. Clone repository
git clone https://github.com/pin0513/dopeman.git ~/DEV/projects/dopeman

# 2. 安裝依賴
cd ~/DEV/projects/dopeman
# Python 3.x required, no additional dependencies

# 3. 執行掃描
cd commands
python3 scan-real-data.py

# 4. 啟動 Dashboard
./start-dashboard.sh
```

### 基本使用

```bash
# 啟動總控台 Dashboard
/dopeman cc

# 檢查 skills 更新
/dopeman check-updates

# 整理開發目錄
/dopeman organize ~/DEV

# 匯出環境配置
/dopeman export-config

# 產生使用報告
/dopeman usage-report

# 搜尋推薦的新 skills
/dopeman discover-skills

# 完整環境健檢
/dopeman health-check
```

---

## 🎛️ Dashboard 總控台

啟動互動式 Web Dashboard 查看環境全貌：

```bash
/dopeman cc
```

Dashboard 會在 `http://localhost:8891` 開啟，提供：

### 統計儀表板
- 📊 全域 Skills、專案 Skills、開發中 Skills
- 📋 全域 Rules、專案 Rules
- 🤖 Agents (Coordinators & Workers)
- 💻 Dev Projects（開發專案）
- ⌨️ Commands（可用指令）

### 功能標籤頁

#### 1. **Skills 標籤**
- 🌍 全域 Skills 列表（83 個）
- 📁 專案 Skills（依專案分組）
- 🔨 開發中 Skills（有 Git Repo 的）
- 🔴 重複 Skills 標記

#### 2. **Agents 標籤**
- 🎯 Coordinators（14 個）
- 👷 Workers（依群組分類）
- 📂 所屬專案標示

#### 3. **Rules 標籤**
- 🌍 全域 Rules（13 個）
- 📁 專案 Rules（26 個）
- 🔗 適用範圍標示

#### 4. **Commands 標籤**
- ⌨️ 所有可用指令列表
- 📝 指令說明

#### 5. **Dev Projects 標籤** ⭐ NEW
- 💻 **13 個開發專案**展示
- 🏷️ **專案類型**分類：
  - 🔵 工作專案（7 個）
  - 🟢 自有開發（2 個）
  - 🟣 GitHub 參考（4 個）
- 🛠️ **技術棧**標籤（.NET/C#、React、Next.js、Python）
- 🔀 **Git 狀態**追蹤（乾淨/未提交）
- 🤖 **Claude Team** 標記
- 📅 **最後 commit** 資訊
- 🚀 **Quick Launch**：
  - 📂 Open in VS Code
  - 🔗 Git Remote（Azure DevOps/GitHub）

#### 6. **分層視圖**
- 📍 Entry Layer（Commands）
- 📍 Coordination Layer（Coordinators）
- 📍 Execution Layer（Workers)

### Dashboard 截圖

```
┌────────────────────────────────────────────────────────────┐
│  🎛️  Skills Control Center                                │
│  真實資料視覺化 - 完整環境掃描結果                           │
├────────────────────────────────────────────────────────────┤
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐        │
│  │ 🌍   │  │ 📁   │  │ 🔨   │  │ 💻   │  │ 🤖   │        │
│  │  83  │  │  87  │  │  4   │  │  13  │  │  39  │        │
│  │Skills│  │Skills│  │Skills│  │Projects│ │Agents│        │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘        │
├────────────────────────────────────────────────────────────┤
│  [ Skills ] [ Agents ] [ Rules ] [ Commands ] [ Dev Projects ] [ 分層視圖 ] │
├────────────────────────────────────────────────────────────┤
│  📂 MAYO-Report-Master                    🔵 工作專案       │
│  📁 DEV/MAYO-Report-Master                                 │
│  技術棧: .NET/C#                                            │
│  🔀 Git: 🟡 未提交  🤖 ✓ Claude Team                       │
│  📅 最後提交: 2026-02-07                                    │
│  "Merged PR 83702: [MR-39] test: 新增報表清單..."          │
│  [ 📂 Open in VS Code ] [ 🔗 Git Remote ]                  │
└────────────────────────────────────────────────────────────┘
```

---

## 📁 專案架構

```
dopeman/
├── .claude/
│   ├── agents/                      # Agent 團隊
│   │   ├── dopeman-coordinator.md   # 總調度者
│   │   ├── skills-management/       # Skills 管理組
│   │   │   ├── skill-tracker.md     # 追蹤更新
│   │   │   └── skill-scout.md       # 探索新 skills
│   │   ├── environment/             # 環境管理組
│   │   │   ├── file-organizer.md    # 目錄整理
│   │   │   └── sync-manager.md      # 跨電腦同步
│   │   └── analytics/               # 分析組
│   │       └── usage-analyst.md     # 使用分析
│   │
│   ├── skills/                      # Skill 定義
│   │   ├── dopeman/SKILL.md         # 主 Skill（同步到全域）
│   │   ├── shared/                  # 共用 Skills
│   │   │   ├── version-comparison/
│   │   │   ├── github-api-operations/
│   │   │   ├── cross-platform-path/
│   │   │   ├── file-classification/
│   │   │   ├── json-registry-manager/
│   │   │   └── user-confirmation/
│   │   └── specialized/             # 專業 Skills
│   │       ├── skill-lineage-tracking/
│   │       ├── file-system-operations/
│   │       ├── skill-discovery/
│   │       ├── environment-sync/
│   │       ├── dopeman-orchestration/
│   │       └── usage-statistics/
│   │
│   └── rules/                       # 團隊規則
│       ├── no-silent-failures.md    # 錯誤必須記錄與通知
│       ├── backup-before-modify.md  # 修改前必須備份
│       ├── idempotent-operations.md # 操作必須冪等
│       ├── log-all-actions.md       # 所有操作必須記錄
│       └── respect-rate-limits.md   # 遵守 API rate limit
│
├── commands/                        # 執行腳本
│   ├── scan-real-data.py           # 環境掃描引擎
│   ├── control-center-real.html    # Dashboard 前端
│   ├── control-center-real-data.json # 掃描資料
│   ├── start-dashboard.sh          # 啟動 Dashboard
│   ├── stop-dashboard.sh           # 停止 Dashboard
│   └── sync-global-skill.sh        # 全域同步工具
│
├── CLAUDE.md                        # 專案說明文件
├── README.md                        # 本檔案
└── .gitignore
```

---

## 🔄 雙版本架構

DopeMAN 同時存在於兩個位置：

### 1. **全域 Skill** (`~/.claude/skills/dopeman/`)
- **用途**：在任何目錄都可呼叫 `/dopeman`
- **內容**：僅 `SKILL.md` 檔案
- **更新**：從專案 Push

### 2. **開發專案** (`~/DEV/projects/dopeman/`)
- **用途**：獨立開發、版本控制、功能擴展
- **內容**：完整團隊結構（agents/skills/rules/commands）
- **更新**：Git 版本控制

### 同步機制

使用 `commands/sync-global-skill.sh` 管理雙向同步：

```bash
cd ~/DEV/projects/dopeman/commands
./sync-global-skill.sh

# 選項
1) Pull  - 全域 → 專案 (從全域更新到專案)
2) Push  - 專案 → 全域 (從專案推送到全域)
3) Diff  - 比較差異
4) Status - 檢查狀態
```

### 開發流程

```bash
# 1. 在專案中開發
cd ~/DEV/projects/dopeman
# 編輯 .claude/skills/dopeman/SKILL.md
git add .
git commit -m "feat: add new feature"
git push

# 2. 推送到全域
./commands/sync-global-skill.sh
# 選擇 2) Push

# 3. 驗證
/dopeman cc  # 測試新功能
```

### 安全機制
- ✅ Push 前自動備份全域版本
- ✅ 差異比較避免誤覆蓋
- ✅ 狀態檢查確保同步
- ✅ Git 版本控制可追蹤變更

---

## 🛠️ 開發指南

### 環境要求

- **Python**: 3.7+
- **Claude Code**: 最新版本
- **Git**: 用於版本控制
- **瀏覽器**: 查看 Dashboard（Chrome/Firefox/Safari）

### 本地開發

```bash
# 1. Clone repository
git clone https://github.com/pin0513/dopeman.git
cd dopeman

# 2. 修改程式碼
# 編輯 .claude/agents/*.md
# 編輯 .claude/skills/*.md
# 編輯 commands/scan-real-data.py

# 3. 測試掃描
cd commands
python3 scan-real-data.py

# 4. 測試 Dashboard
./start-dashboard.sh
# 開啟 http://localhost:8891/control-center-real.html

# 5. 提交變更
git add .
git commit -m "feat: your feature"
git push
```

### 新增 Agent

1. 在 `.claude/agents/` 對應群組建立 `.md` 檔案
2. 使用 YAML frontmatter：
   ```markdown
   ---
   name: Agent Name
   description: One sentence description
   model: sonnet
   ---
   ```
3. 更新 `CLAUDE.md` 的團隊說明

### 新增 Skill

1. 在 `.claude/skills/shared/` 或 `specialized/` 建立目錄
2. 建立 `SKILL.md` 檔案
3. 定義 skill 功能與使用時機
4. 在需要的 agent 中引用

### 新增 Rule

1. 在 `.claude/rules/` 建立 `.md` 檔案
2. 使用 YAML frontmatter 定義適用範圍
3. 說明規則內容、違反判定、例外情況

---

## 📚 命令參考

### 主要命令

| 命令 | 別名 | 說明 |
|------|------|------|
| `/dopeman control-center` | `cc` | 開啟 Skills 總控台 Dashboard |
| `/dopeman stop-dashboard` | `scc` | 停止 Dashboard 伺服器 |
| `/dopeman check-updates` | - | 檢查 skills 更新 |
| `/dopeman organize` | - | 整理指定目錄 |
| `/dopeman export-config` | - | 匯出環境配置 |
| `/dopeman import-config` | - | 匯入環境配置 |
| `/dopeman usage-report` | - | 產生使用報告 |
| `/dopeman discover-skills` | - | 搜尋推薦的新 skills |
| `/dopeman health-check` | - | 完整環境健檢 |

### 掃描引擎

```bash
# 完整環境掃描
cd commands
python3 scan-real-data.py

# 掃描結果
# → control-center-real-data.json
```

掃描內容：
- ✅ 全域 Skills（83 個）
- ✅ 專案 Skills（87 個）
- ✅ 開發中 Skills（4 個）
- ✅ **開發專案（13 個）** ⭐ NEW
- ✅ 全域 Rules（13 個）
- ✅ 專案 Rules（26 個）
- ✅ Agents（39 個）
- ✅ Commands（8 個）

### Dashboard 管理

```bash
# 啟動 Dashboard
./start-dashboard.sh
# → http://localhost:8891/control-center-real.html

# 停止 Dashboard
./stop-dashboard.sh

# 檢查狀態
cat /tmp/dopeman-dashboard.pid
tail -f /tmp/dopeman-dashboard.log
```

---

## 🤝 貢獻指南

我們歡迎各種形式的貢獻！

### 如何貢獻

1. **Fork** 本專案
2. 建立 **Feature Branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** 變更 (`git commit -m 'feat: add amazing feature'`)
4. **Push** 到分支 (`git push origin feature/amazing-feature`)
5. 開啟 **Pull Request**

### Commit 訊息格式

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
feat: 新增功能
fix: 修復 Bug
docs: 文件更新
refactor: 重構
test: 測試
chore: 維護性工作
```

### 貢獻方向

- 🐛 **Bug 修復**：回報或修復問題
- ✨ **新功能**：提出或實作新功能
- 📝 **文件**：改善 README、CLAUDE.md、註解
- 🎨 **Dashboard**：優化 UI/UX、新增視覺化圖表
- 🧪 **測試**：新增測試案例
- 🌐 **國際化**：新增語言支援

---

## 📄 License

MIT License - 詳見 [LICENSE](LICENSE) 檔案

---

## 🙏 致謝

- [Claude Code](https://claude.ai/code) - AI-powered coding assistant
- [Anthropic](https://www.anthropic.com/) - Claude AI 開發團隊
- 所有貢獻者與使用者 ❤️

---

## 📞 聯絡方式

- **GitHub Issues**: [https://github.com/pin0513/dopeman/issues](https://github.com/pin0513/dopeman/issues)
- **Discussions**: [https://github.com/pin0513/dopeman/discussions](https://github.com/pin0513/dopeman/discussions)

---

## 🗺️ Roadmap

### v1.1 (規劃中)
- [ ] Skills 版本比較與 diff 視圖
- [ ] 一鍵更新所有 skills
- [ ] Skills 使用趨勢圖表
- [ ] 專案健康度評分

### v1.2 (規劃中)
- [ ] Web UI 取代 CLI（React + Next.js）
- [ ] Skills Marketplace 整合
- [ ] 自動化測試框架
- [ ] Docker 支援

### v2.0 (願景)
- [ ] AI 驅動的 Skill 推薦
- [ ] 團隊協作功能
- [ ] Cloud Sync 支援
- [ ] Skills 效能分析

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/pin0513">pin0513</a>
</p>

<p align="center">
  <a href="#top">⬆️ 回到頂部</a>
</p>
