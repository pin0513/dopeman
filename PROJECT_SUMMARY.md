# DopeMAN 專案摘要

**建立日期**: 2026-02-08
**初始 Commit**: 3c36751

---

## 專案定位

DopeMAN 是一個智能環境管理秘書團隊，專注於 Claude Code skills 的全生命週期管理。

---

## 雙版本架構

### 全域 Skill (Production)

```
位置: ~/.claude/skills/dopeman/SKILL.md
用途: 在任何目錄都可呼叫 /dopeman
內容: 主 skill 定義檔
更新: 從專案 push
```

### 開發專案 (Development)

```
位置: ~/DEV/projects/dopeman/
用途: 獨立開發、版本控制、功能擴展
內容: 完整團隊結構
版控: Git repository
```

---

## 專案統計

### 團隊規模

| 類別 | 數量 | 位置 |
|------|------|------|
| Agents | 6 | `.claude/agents/` |
| Rules | 5 | `.claude/rules/` |
| Skills | 13 | `.claude/skills/` |
| Commands | 14 | `commands/` |

### 檔案統計

- **總檔案**: 39 files
- **總行數**: 9,838 lines
- **初始 Commit**: 3c36751

---

## 核心功能

### 1. Skills Control Center Dashboard

**啟動方式**:
```bash
/dopeman cc           # 全域指令
./commands/start-dashboard.sh  # 本機腳本
```

**Dashboard URL**: http://localhost:8891/control-center-real.html

**功能**:
- ✅ 視覺化 82 個全域 skills
- ✅ 管理 86 個專案 skills
- ✅ 追蹤 39 個 agents (14 coordinators + 25 workers)
- ✅ 檢視 13 個全域 rules + 26 個專案 rules
- ✅ 瀏覽 8 個 commands
- ✅ 階層視圖 (Entry → Coordination → Execution → Resource)

### 2. 全域同步機制

**同步工具**: `commands/sync-global-skill.sh`

**操作模式**:
- **Pull** (全域 → 專案): 從全域更新到專案
- **Push** (專案 → 全域): 從專案推送到全域 (自動備份)
- **Diff**: 比較兩邊差異
- **Status**: 檢查同步狀態

**安全機制**:
- ✅ Push 前自動備份全域版本
- ✅ 差異比較避免誤覆蓋
- ✅ Git 版本控制追蹤所有變更

### 3. 環境掃描

**掃描工具**: `commands/scan-real-data.py`

**掃描範圍**:
- Global Skills
- Project Skills
- Development Skills (with repos)
- Global Rules
- Project Rules
- Agents (Coordinators & Workers)
- Commands

**輸出**: `commands/control-center-real-data.json`

---

## 開發工作流程

### 步驟 1: 修改專案

```bash
cd ~/DEV/projects/dopeman

# 編輯 skill 定義
vim .claude/skills/dopeman/SKILL.md

# 或編輯其他檔案
vim commands/start-dashboard.sh
```

### 步驟 2: Commit 變更

```bash
git add .
git commit -m "feat: add new feature"
```

### 步驟 3: 同步到全域

```bash
./commands/sync-global-skill.sh
# 選擇 2) Push - 專案 → 全域
```

### 步驟 4: 測試

```bash
# 測試全域 skill
/dopeman cc

# 或測試特定命令
/dopeman check-updates
```

---

## 命令速查表

### Dashboard 管理

| 命令 | 別名 | 說明 |
|------|------|------|
| `/dopeman control-center` | `cc` | 開啟 Dashboard |
| `/dopeman stop-dashboard` | `scc` | 停止 Dashboard |

### 同步管理

```bash
# 檢查狀態
./commands/sync-global-skill.sh  # 選擇 4

# 推送到全域
./commands/sync-global-skill.sh  # 選擇 2

# 從全域拉取
./commands/sync-global-skill.sh  # 選擇 1

# 查看差異
./commands/sync-global-skill.sh  # 選擇 3
```

### 環境掃描

```bash
# 重新掃描環境
python3 commands/scan-real-data.py

# 檢視結果
cat commands/control-center-real-data.json | jq .
```

---

## 資料位置

### Memory 資料

```
~/.claude/memory/dopeman/
├── skills-registry.json         ← Skill 來源與版本記錄
├── skill-recommendations.json   ← 推薦的新 skills
├── usage-report.json            ← 使用統計報告
├── operation.log                ← 操作日誌
└── github-cache.json            ← GitHub API 快取
```

### Runtime 資料

```
/tmp/
├── dopeman-dashboard.pid  ← Dashboard 伺服器 PID
└── dopeman-dashboard.log  ← Dashboard 伺服器日誌
```

### Git Repository

```
~/DEV/projects/dopeman/
├── .git/                        ← Git 版本控制
├── .gitignore                   ← 排除規則
└── PROJECT_SUMMARY.md           ← 本文件
```

---

## 技術棧

| 層級 | 技術 |
|------|------|
| 後端 | Python 3.9+, Bash |
| 前端 | HTML5, CSS3, JavaScript (ES6+) |
| 伺服器 | Python http.server (port 8891) |
| 版本控制 | Git |
| 部署模式 | Subagent |

---

## 未來規劃

### Phase 1: 基礎建設 ✅

- ✅ 專案結構建立
- ✅ 雙版本架構
- ✅ 同步機制
- ✅ Dashboard 界面
- ✅ Git 版本控制

### Phase 2: 功能擴展 (規劃中)

- [ ] GitHub Repository 建立
- [ ] 自動化測試
- [ ] CI/CD Pipeline
- [ ] Skills 市場整合
- [ ] 使用分析儀表板

### Phase 3: 社群化 (未來)

- [ ] 公開 GitHub Repo
- [ ] 文件網站
- [ ] 社群貢獻指南
- [ ] Plugin 系統

---

## 維護日誌

### 2026-02-08

- ✅ 初始化專案
- ✅ 建立完整團隊結構 (6 agents, 5 rules, 13 skills)
- ✅ 實作 Skills Control Center Dashboard
- ✅ 建立全域同步機制
- ✅ 第一次 Git commit (3c36751)

---

## 快速參考

### 最常用命令

```bash
# Dashboard
/dopeman cc          # 開啟
/dopeman scc         # 停止

# 同步
cd ~/DEV/projects/dopeman/commands
./sync-global-skill.sh     # Push/Pull

# 掃描
python3 commands/scan-real-data.py

# Git
git status
git add .
git commit -m "feat: description"
```

### 重要路徑

```bash
# 專案
~/DEV/projects/dopeman/

# 全域 Skill
~/.claude/skills/dopeman/SKILL.md

# Dashboard
http://localhost:8891/control-center-real.html
```

---

**維護者**: DopeMAN Team
**最後更新**: 2026-02-08
