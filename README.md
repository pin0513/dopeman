# DopeThingsMan

智能環境管理秘書團隊，負責 skills 管理、目錄整理、使用分析與跨電腦同步。

## 專案結構

```
dopethingsman/
├── .claude/                      ← 團隊結構
│   ├── agents/                   ← 6 個 agent
│   │   ├── dopethingsman-coordinator.md
│   │   ├── analytics/
│   │   │   └── usage-analyst.md
│   │   ├── environment/
│   │   │   ├── file-organizer.md
│   │   │   └── sync-manager.md
│   │   └── skills-management/
│   │       ├── skill-scout.md
│   │       └── skill-tracker.md
│   ├── rules/                    ← 5 個 rule
│   │   ├── backup-before-modify.md
│   │   ├── idempotent-operations.md
│   │   ├── log-all-actions.md
│   │   ├── no-silent-failures.md
│   │   └── respect-rate-limits.md
│   └── skills/                   ← 技能庫
│       ├── dopethingsman/        ← 主 skill (同步到全域)
│       │   └── SKILL.md
│       ├── shared/               ← 6 個共用 skill
│       └── specialized/          ← 6 個專用 skill
├── commands/                     ← 命令腳本
│   ├── check-updates.sh
│   ├── init-registry.sh
│   ├── validate-structure.sh
│   ├── sync-global-skill.sh      ← 全域同步腳本
│   ├── scan-real-data.py         ← 環境掃描
│   ├── start-dashboard.sh        ← 啟動 Dashboard
│   ├── stop-dashboard.sh         ← 停止 Dashboard
│   ├── control-center-real.html  ← Dashboard 界面
│   ├── control-center-real-data.json ← 掃描資料
│   └── *.md                      ← 規格文件
├── CLAUDE.md                     ← 專案說明
├── README.md                     ← 本文件
└── .gitignore

全域位置:
~/.claude/skills/dopethingsman/SKILL.md  ← 全域 skill (從專案同步)
```

## 雙版本架構

### 全域 Skill

**位置**：`~/.claude/skills/dopethingsman/`
- 包含：`SKILL.md` (主 skill 定義)
- 用途：在任何目錄都可呼叫 `/dopethingsman`
- 更新方式：從專案 push

### 開發專案

**位置**：`~/DEV/projects/dopethingsman/`
- 包含：完整團隊結構 (agents/skills/rules/commands)
- 用途：獨立開發、版本控制、功能擴展
- 更新方式：git 版本控制

## 快速開始

### 1. 啟動 Control Center Dashboard

```bash
cd ~/DEV/projects/dopethingsman

# 啟動 Dashboard (自動掃描並開啟瀏覽器)
./commands/start-dashboard.sh

# 或使用全域指令 (需先同步到全域)
/dopethingsman cc

# 停止 Dashboard
./commands/stop-dashboard.sh
# 或
/dopethingsman scc
```

Dashboard URL: http://localhost:8891/control-center-real.html

### 2. 同步全域 Skill

```bash
cd ~/DEV/projects/dopethingsman/commands

# 執行同步腳本
./sync-global-skill.sh

# 選項：
# 1) Pull  - 全域 → 專案
# 2) Push  - 專案 → 全域 (建議在修改後執行)
# 3) Diff  - 比較差異
# 4) Status - 檢查同步狀態
```

### 3. 開發流程

```bash
# 1. 修改專案版本
cd ~/DEV/projects/dopethingsman
vim .claude/skills/dopethingsman/SKILL.md

# 2. Commit 變更
git add .
git commit -m "feat: add new command"

# 3. Push 到全域
./commands/sync-global-skill.sh  # 選擇 2) Push

# 4. 測試全域 skill
/dopethingsman <command>
```

## 主要功能

### 1. Skills Control Center

**視覺化管理介面**：
- 82 個全域 skills
- 86 個專案 skills
- 39 個 agents (14 coordinators + 25 workers)
- 13 個全域 rules
- 26 個專案 rules
- 8 個 commands

**功能**：
- 階層視圖 (Entry → Coordination → Execution → Resource)
- 分類瀏覽 (Skills/Agents/Rules/Commands/Layers)
- 搜尋與過濾
- 即時掃描

### 2. 環境管理

- 目錄分類 (產出區/工作區/參考區/暫存區)
- Skills 生命週期管理
- 使用分析優化
- 跨電腦同步

### 3. Skills 市場探索

- 發現熱門新 skills
- 評估品質 (Stars, 活躍度, 文件, 測試)
- 推薦引入

## 命令別名

| 完整命令 | 別名 | 說明 |
|---------|------|------|
| `control-center` | `cc` | 開啟 Skills 總控台 Dashboard |
| `stop-dashboard` | `scc` | 停止 Dashboard 伺服器 |

```bash
/dopethingsman cc    # 快速開啟 Dashboard
/dopethingsman scc   # 快速停止 Dashboard
```

## 技術棧

- **後端**: Python 3 (掃描), Bash (腳本)
- **前端**: HTML/CSS/JavaScript (Dashboard)
- **伺服器**: Python http.server
- **版本控制**: Git
- **部署**: Subagent 模式

## 資料位置

```
~/.claude/memory/dopethingsman/
├── skills-registry.json         ← Skill 來源與版本記錄
├── skill-recommendations.json   ← 推薦的新 skills
├── usage-report.json            ← 使用統計報告
├── operation.log                ← 操作日誌
└── github-cache.json            ← GitHub API 快取

/tmp/
├── dopethingsman-dashboard.pid  ← Dashboard 伺服器 PID
└── dopethingsman-dashboard.log  ← Dashboard 伺服器日誌
```

## 開發指南

### 修改主 Skill

```bash
# 編輯專案版本
vim .claude/skills/dopethingsman/SKILL.md

# 推送到全域
./commands/sync-global-skill.sh  # 選擇 2) Push
```

### 添加新命令

1. 在 `commands/` 目錄建立新腳本
2. 更新 `SKILL.md` 的命令表格
3. 同步到全域

### 修改 Dashboard

```bash
# 編輯界面
vim commands/control-center-real.html

# 重新掃描資料
python3 commands/scan-real-data.py

# 重啟 Dashboard
./commands/stop-dashboard.sh
./commands/start-dashboard.sh
```

## 貢獻指南

1. Fork 專案 (未來可建立 GitHub repo)
2. 建立 feature 分支
3. Commit 變更
4. Push 到分支
5. 建立 Pull Request

## 授權

MIT License

## 維護者

DopeThingsMan Team

---

**版本**: v1.0.0
**建立日期**: 2026-02-08
**專案位置**: `/Users/paul_huang/DEV/projects/dopethingsman`
