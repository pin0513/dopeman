# Skills Control Center - 功能規格

## 概述

Skills Control Center 是 DopeMAN 的核心管理介面，提供完整的技能掃描、分類、整合與優化功能。

---

## 資料結構設計

### 主要資料模型

```json
{
  "version": "1.0.0",
  "last_scan": "2026-02-08T10:30:00Z",
  "categories": {
    "global": {
      "path": "~/.claude/skills",
      "count": 42,
      "skills": [...]
    },
    "projects": {
      "count": 5,
      "items": [
        {
          "project_path": "~/DEV/MAYO-Report-Master",
          "skills_path": ".claude/skills",
          "skills": [...]
        }
      ]
    },
    "development": {
      "count": 3,
      "items": [
        {
          "name": "dopeman",
          "path": "~/DEV/projects/dopeman",
          "repo": "https://github.com/user/dopeman",
          "branch": "main",
          "dirty": false,
          "stars": 156
        }
      ]
    },
    "candidates": {
      "count": 5,
      "items": [
        {
          "name": "playwright-helper",
          "repo": "https://github.com/user/playwright-helper",
          "stars": 1200,
          "score": 78,
          "reason": "可節省 60% E2E 測試時間"
        }
      ]
    }
  },
  "dependency_graph": {
    "skill_name": {
      "used_by_agents": ["agent1", "agent2"],
      "used_by_skills": ["skill2"],
      "used_by_projects": ["project1"],
      "depends_on": ["dependency1"]
    }
  },
  "duplicates": [
    {
      "skill_name": "slide-consult",
      "locations": [
        "~/.claude/skills/slide-consult",
        "~/.claude/skills/slide_consult/slide-consult"
      ],
      "recommendation": "保留 ~/.claude/skills/slide-consult，移除重複版本"
    }
  ],
  "conflicts": [
    {
      "type": "version_mismatch",
      "skill": "team001",
      "global_version": "2.0.0",
      "project_version": "1.5.0",
      "project": "~/DEV/MAYO-Report-Master"
    }
  ]
}
```

---

## 核心功能規格

### 1. 掃描引擎（Scan Engine）

#### 1.1 全域 Skills 掃描

**掃描路徑**：`~/.claude/skills/**/*`

**掃描內容**：
- Skill 名稱與描述
- YAML frontmatter（version, source）
- 檔案修改時間
- Git 狀態（如果是 repo）

**輸出**：
```json
{
  "name": "team001",
  "path": "~/.claude/skills/team001",
  "type": "team",
  "source": "local",
  "version": "2.0.0",
  "last_modified": "2026-02-07",
  "has_git": false,
  "used_by": ["agent1", "agent2"]
}
```

#### 1.2 專案 Skills 掃描

**掃描策略**：
1. 查找所有 `.claude/` 目錄（排除 global）
2. 檢查 `skills/` 子目錄
3. 比對是否與 global skills 重複

**輸出**：
```json
{
  "project_path": "~/DEV/MAYO-Report-Master",
  "skills_count": 8,
  "skills": [...],
  "duplicates": ["team001-mayo-coding-standard"],
  "unique": ["mayo-specific-skill"]
}
```

#### 1.3 開發中 Skills 掃描

**識別條件**：
- 有 `.git/` 目錄
- 或有 `package.json` / `pyproject.toml`
- 或在 `~/DEV/projects/` 下

**掃描內容**：
- Git remote URL
- 當前分支
- Dirty 狀態（未 commit 變更）
- GitHub 資訊（stars, forks, last update）

#### 1.4 候選 Skills 探索

**來源**：
1. GitHub Search API（keyword: "claude-code skill"）
2. Awesome Lists（awesome-claude-code）
3. 社群推薦（Reddit, Twitter）

**評分機制**：
```
Total Score =
  Stars (10%) +
  Activity (30%) +
  Documentation (30%) +
  Tests (20%) +
  Community (10%)
```

**過濾條件**：
- Score ≥ 60
- Last commit within 90 days
- Has README

---

### 2. 分層結構視圖（Hierarchy View）

#### 樹狀圖生成

**輸出格式**（ASCII）：
```
🌍 Global Skills (42)
├─ 🎯 team001 (v2.0.0)
│  └─ 📦 Used by: agent1, agent2
├─ 📊 slide-consult (v1.5.0)
│  └─ 🔗 Depends on: slide-image, slide-maker
└─ ⚠️  old-skill (deprecated, 180d unused)

📁 Project Skills (12)
├─ ~/DEV/MAYO-Report-Master
│  ├─ team001-mayo-coding-standard (forked from global)
│  └─ mayo-specific-skill (unique)
└─ ~/DEV/projects/dopeman
   └─ dopeman-coordinator

🔨 Development Skills (3)
├─ dopeman (github.com/user/repo, 156⭐)
├─ my-custom-skill (local, dirty)
└─ research-skill (no remote)

💡 Recommended Skills (5)
├─ playwright-helper (1.2k⭐, Score: 78)
└─ claude-tdd (800⭐, Score: 65)
```

#### 來源追蹤

**繼承鏈顯示**：
```
upstream: github.com/user/base-skill (v1.5.0)
    ↓ forked
global: ~/.claude/skills/base-skill (v1.5.0, modified)
    ↓ used by
project: ~/DEV/project/.claude/skills/base-skill (v1.5.0)
```

---

### 3. 依賴關係檢查（Dependency Check）

#### 依賴類型

**1. Agent 依賴**：
```
team001 skill
  ├─ Used by: dev-team-lead agent
  ├─ Used by: dev-team-pm agent
  └─ Used by: dev-team-qa agent
```

**2. Skill 間依賴**：
```
slide-consult
  ├─ Depends on: slide-image
  ├─ Depends on: slide-maker
  └─ Depends on: slide-qa
```

**3. 專案依賴**：
```
team001
  ├─ Used in: ~/DEV/MAYO-Report-Master
  ├─ Used in: ~/DEV/MAYOForm-WebAdmin
  └─ Not used in: ~/DEV/demo-project
```

#### 衝突偵測

**版本衝突**：
```
⚠️  Version Conflict Detected:
  Skill: team001
  Global: v2.0.0
  ~/DEV/project-a: v1.5.0
  ~/DEV/project-b: v2.0.0

  Recommendation: Update project-a to v2.0.0
```

**重複定義衝突**：
```
⚠️  Duplicate Definition:
  Skill: slide-consult
  Location 1: ~/.claude/skills/slide-consult
  Location 2: ~/.claude/skills/slide_consult/slide-consult

  Recommendation: Keep Location 1, remove Location 2
```

---

### 4. 智能整合（Smart Consolidation）

#### 整合策略

**重複 Skills 合併**：
1. 偵測重複（名稱相同或內容相似度 > 80%）
2. 比對版本（選擇最新版本）
3. 檢查依賴（確保無 breaking changes）
4. 備份舊版（`.backup/{timestamp}/`）
5. 執行合併
6. 更新所有引用

**清理無用 Skills**：
- 識別 180 天未使用的 skills
- 檢查是否有 agent 依賴
- 提供歸檔選項（移至 `.archive/`）

#### 安全機制

**備份策略**：
```
執行前：
  1. 建立完整備份 → .backup/2026-02-08_103045/
  2. 記錄操作計畫 → consolidation-plan.json
  3. 生成回滾腳本 → rollback.sh

執行中：
  1. 逐項檢查依賴
  2. 每個操作後驗證
  3. 發現問題立即停止

執行後：
  1. 驗證所有 agents 可正常啟動
  2. 驗證專案 skills 未被破壞
  3. 生成整合報告
```

**依賴保護**：
- 檢查 `used_by` 欄位
- 檢查專案 `.claude/skills/` 引用
- 檢查 CLAUDE.md 中的 skill 名稱
- 禁止刪除有依賴的 skills

**專案保護**：
- 專案 skills 只影響該專案
- 不自動同步到 global
- 需明確用戶確認才能移動

**Repo 保護**：
- 有 `.git/` 的 skills 不自動移動
- Dirty 狀態的 skills 提示先 commit
- Remote repo 的 skills 提示先 push

---

### 5. 溯源報告（Traceability Report）

#### 報告內容

**Markdown 格式**：

```markdown
# Skills Traceability Report

生成時間：2026-02-08 10:30:45
掃描範圍：全域、專案、開發中、候選

---

## 📊 總覽

| 類別 | 數量 | 狀態 |
|------|------|------|
| 全域 Skills | 42 | ✓ |
| 專案 Skills | 12 | ✓ |
| 開發中 Skills | 3 | ⚠️ 1 dirty |
| 推薦 Skills | 5 | - |
| **總計** | **62** | - |

---

## 🌍 全域 Skills

### team001 (v2.0.0)

- **位置**：`~/.claude/skills/team001`
- **來源**：local
- **最後修改**：2026-02-07
- **使用者**：
  - Agent: dev-team-lead
  - Agent: dev-team-pm
  - Project: ~/DEV/MAYO-Report-Master

### slide-consult (v1.5.0)

- **位置**：`~/.claude/skills/slide-consult`
- **來源**：local
- **依賴**：slide-image, slide-maker, slide-qa
- **使用者**：
  - Agent: slide-coordinator

---

## 📁 專案 Skills

### ~/DEV/MAYO-Report-Master

#### team001-mayo-coding-standard

- **來源**：Forked from global team001 (v2.0.0)
- **客製化**：新增 MAYO 品牌規範
- **修改記錄**：
  - 2026-02-05: 新增 UI 2.0 規範
  - 2026-01-20: 新增 API 命名規則

---

## 🔨 開發中 Skills

### dopeman

- **位置**：`~/DEV/projects/dopeman`
- **Repo**：github.com/user/dopeman
- **Branch**：main
- **Status**：Clean (無未 commit 變更)
- **GitHub**：156 ⭐, 12 forks

---

## ⚠️ 問題與建議

### 重複 Skills

1. **slide-consult**
   - Location 1: ~/.claude/skills/slide-consult
   - Location 2: ~/.claude/skills/slide_consult/slide-consult
   - **建議**：保留 Location 1，移除 Location 2

### 版本衝突

1. **team001**
   - Global: v2.0.0
   - Project ~/DEV/old-project: v1.5.0
   - **建議**：更新專案版本

### 無使用 Skills

1. **old-skill-1** (180 天未使用)
   - 無 agent 依賴
   - **建議**：歸檔或移除

---

## 📈 使用統計

| Skill | 使用次數 (30天) | 平均執行時間 |
|-------|----------------|--------------|
| team001 | 42 | 2.3s |
| slide-consult | 28 | 5.1s |
| dev-team-lead | 15 | 3.8s |

---

## 🔗 依賴圖譜

```
team001
  ├─ dev-team-lead
  ├─ dev-team-pm
  └─ dev-team-qa

slide-consult
  ├─ slide-image
  ├─ slide-maker
  └─ slide-qa
```

---

生成工具：DopeMAN v1.0.0
```

#### HTML 報告

提供可互動的 HTML 版本，包含：
- 可摺疊的樹狀圖
- 點擊查看詳細資訊
- 依賴圖譜視覺化（使用 D3.js）
- 搜尋與過濾功能

---

### 6. 安全檢查（Safety Check）

#### 檢查清單

**專案關聯檢查**：
```bash
✓ 檢查所有專案 .claude/skills 引用
✓ 檢查 CLAUDE.md 中的 skill 名稱
✓ 檢查 agents/*.md 中的 skill 引用
✓ 檢查 skills/*/SKILL.md 中的依賴
```

**Repo 關聯檢查**：
```bash
✓ 檢查 .git/config remote URL
✓ 檢查 dirty 狀態 (git status)
✓ 檢查未 push 的 commits
✓ 檢查 GitHub API (stars, forks, issues)
```

**備份機制檢查**：
```bash
✓ 檢查 .backup/ 目錄存在
✓ 檢查磁碟空間充足
✓ 檢查備份檔案完整性 (checksum)
✓ 檢查回滾腳本可執行
```

**依賴完整性檢查**：
```bash
✓ 檢查所有 used_by 關係有效
✓ 檢查所有 depends_on skills 存在
✓ 檢查循環依賴
✓ 檢查孤立 skills（無任何依賴）
```

#### 風險評估

**風險等級**：
- **Low**: 只影響個人全域 skills
- **Medium**: 影響單一專案 skills
- **High**: 影響多個專案或有 Git repo
- **Critical**: 影響生產環境或有外部依賴

**操作前提示**：
```
⚠️  High Risk Operation Detected

將要執行：移除 skill "old-skill"
影響範圍：
  - 2 個專案引用此 skill
  - 1 個 agent 依賴此 skill
  - 有未 commit 的變更

建議：
  1. 先 commit 變更
  2. 更新依賴的 agents
  3. 更新專案引用

繼續執行？ [y/N]
```

---

## 實作計畫

### Phase 1: 掃描引擎（2-3 天）

**任務**：
- [ ] 實作 global skills 掃描
- [ ] 實作 project skills 掃描
- [ ] 實作 development skills 掃描
- [ ] 實作 candidate skills 探索
- [ ] 建立資料模型與 JSON schema

**交付物**：
- `lib/scanner/global-scanner.ts`
- `lib/scanner/project-scanner.ts`
- `lib/scanner/dev-scanner.ts`
- `lib/scanner/candidate-scout.ts`
- `schemas/control-center-data.json`

### Phase 2: 分層視圖（1-2 天）

**任務**：
- [ ] 實作 ASCII 樹狀圖生成
- [ ] 實作來源追蹤
- [ ] 實作繼承鏈展示
- [ ] 建立互動式終端 UI（blessed.js）

**交付物**：
- `lib/views/hierarchy-view.ts`
- `lib/views/ascii-tree.ts`
- `lib/views/interactive-ui.ts`

### Phase 3: 依賴分析（2-3 天）

**任務**：
- [ ] 實作依賴圖譜生成
- [ ] 實作衝突偵測
- [ ] 實作循環依賴檢查
- [ ] 建立依賴視覺化（D3.js）

**交付物**：
- `lib/analyzer/dependency-analyzer.ts`
- `lib/analyzer/conflict-detector.ts`
- `templates/dependency-graph.html`

### Phase 4: 智能整合（3-4 天）

**任務**：
- [ ] 實作重複 skills 偵測
- [ ] 實作安全合併機制
- [ ] 實作備份與回滾
- [ ] 實作依賴保護檢查

**交付物**：
- `lib/consolidator/duplicate-detector.ts`
- `lib/consolidator/safe-merger.ts`
- `lib/consolidator/backup-manager.ts`
- `lib/safety/dependency-guard.ts`

### Phase 5: 報告生成（1-2 天）

**任務**：
- [ ] 實作 Markdown 報告生成
- [ ] 實作 HTML 互動報告
- [ ] 實作使用統計分析
- [ ] 建立報告模板

**交付物**：
- `lib/reporter/markdown-reporter.ts`
- `lib/reporter/html-reporter.ts`
- `templates/traceability-report.html`

### Phase 6: 安全檢查（2 天）

**任務**：
- [ ] 實作專案關聯檢查
- [ ] 實作 Repo 關聯檢查
- [ ] 實作風險評估
- [ ] 建立安全確認機制

**交付物**：
- `lib/safety/project-guard.ts`
- `lib/safety/repo-guard.ts`
- `lib/safety/risk-assessor.ts`

---

## 命令列介面設計

### 主命令

```bash
/dopeman control-center
```

**啟動互動式 UI**：
```
┌─────────────────────────────────────────┐
│  DopeMAN - Skills Control Center │
├─────────────────────────────────────────┤
│                                         │
│  [1] 🔍 掃描所有 Skills                 │
│  [2] 🌳 檢視分層結構                    │
│  [3] 🔗 檢查依賴關係                    │
│  [4] 🔄 智能整合                        │
│  [5] 📊 生成溯源報告                    │
│  [6] 🛡️  安全檢查                       │
│  [7] ⚙️  設定                           │
│  [0] ❌ 退出                            │
│                                         │
└─────────────────────────────────────────┘

請選擇操作 (0-7): _
```

### 子命令

```bash
# 掃描
/dopeman control-center scan
/dopeman control-center scan --type=global
/dopeman control-center scan --type=projects
/dopeman control-center scan --type=dev

# 檢視
/dopeman control-center view hierarchy
/dopeman control-center view dependencies

# 整合
/dopeman control-center consolidate --dry-run
/dopeman control-center consolidate --confirm

# 報告
/dopeman control-center report --format=markdown
/dopeman control-center report --format=html

# 檢查
/dopeman control-center check safety
/dopeman control-center check conflicts
```

---

## 資料位置

```
~/.claude/memory/dopeman/
├── control-center-data.json       ← 主要資料檔案
├── dependency-graph.json          ← 依賴圖譜
├── scan-cache.json                ← 掃描快取
├── consolidation-plan.json        ← 整合計畫
├── reports/
│   ├── traceability-2026-02-08.md
│   └── traceability-2026-02-08.html
└── .backup/
    └── 2026-02-08_103045/
        ├── skills-registry.json
        └── rollback.sh
```

---

## 效能考量

### 快取機制

- **掃描快取**：有效期 1 小時
- **GitHub API 快取**：有效期 6 小時
- **依賴圖譜快取**：有效期 30 分鐘

### 批次處理

- GitHub API：批次請求（最多 100 repos/次）
- 檔案掃描：並行處理（workers = CPU cores）
- 大型專案：增量掃描（只檢查變更檔案）

### 進度顯示

```
🔍 掃描中... [████████████░░░░░░░░] 60% (30/50)
   目前：檢查專案 ~/DEV/MAYO-Report-Master
   預估剩餘：30 秒
```

---

## 錯誤處理

### 錯誤級別

- **INFO**：掃描到無效 skill，跳過
- **WARNING**：發現衝突，提供建議
- **ERROR**：操作失敗，回滾變更
- **CRITICAL**：資料損壞，立即停止

### 錯誤通知

- 記錄到 `operation.log`
- 顯示在終端 UI
- 發送 Teams 通知（CRITICAL 級別）

---

## 測試策略

### 單元測試

- 掃描器測試（mock 檔案系統）
- 依賴分析測試（mock 資料）
- 整合邏輯測試

### 整合測試

- 完整掃描流程
- 整合與回滾流程
- 報告生成流程

### E2E 測試

- 互動式 UI 測試（使用 blessed-contrib）
- 命令列測試（spawn child process）

---

**版本**：v1.0.0
**建立日期**：2026-02-08
**維護者**：DopeMAN Team
