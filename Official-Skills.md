# DopeMAN 官方 Skills/Teams 完整名單

> 此清單已整合到 `dopeman-app/commands/official-catalog.json`
> 可透過 `./install-official.py` 自動安裝與管理

---

## 0️⃣ Anthropic 官方 Skills（16 個）

**優先級**: ⭐⭐⭐⭐⭐ (最高)
**來源**: https://github.com/anthropics/skills
**自動更新**: ✅

### 文件處理 (4 個)
- **docx** - Word 文件建立與編輯
- **pdf** - PDF 操作與表單提取
- **pptx** - PowerPoint 簡報製作
- **xlsx** - Excel 試算表處理

### 開發工具 (5 個)
- **mcp-builder** - Model Context Protocol 伺服器建構
- **skill-creator** - Skill 建立器
- **webapp-testing** - Web App 自動化測試
- **web-artifacts-builder** - Web Artifacts 建構器
- **frontend-design** - 前端 UI/UX 設計

### 創意工具 (3 個)
- **algorithmic-art** - 演算法藝術生成
- **canvas-design** - Canvas 視覺設計
- **theme-factory** - 主題與樣式生成器

### 企業協作 (4 個)
- **brand-guidelines** - 品牌視覺規範管理
- **doc-coauthoring** - 文件協作編輯
- **internal-comms** - 企業內部溝通管理
- **slack-gif-creator** - Slack GIF 動畫建立器

---

## 1️⃣ 官方核心專案（3 個）

**優先級**: ⭐⭐⭐⭐ (高)
**install_type**: `global_link` / `project`
**自動更新**: ✅ / ❌

| 專案 | 類型 | 說明 | 連結 |
|------|------|------|------|
| **DopeMAN** | Skill | 智能環境管理秘書團隊 | [GitHub](https://github.com/pin0513/dopeman) |
| **CLAUDE-PUNK** | Team | Claude 客製化開發框架 | [GitHub](https://github.com/chemistrywow31/CLAUDE-PUNK) |
| **A-Team** | Team | 多功能開發團隊 | [GitHub](https://github.com/chemistrywow31/A-Team) |

---

## 2️⃣ 專業級 Skills（5 個）

**優先級**: ⭐⭐⭐ (中高)
**install_type**: `global_link`
**自動更新**: ✅

### 商業策略
- **product-strategy-coach** - 軟體產品策略教練
  - 連結：https://github.com/pin0513/product-strategy-coach
  - 標籤：`strategy`, `product`, `coach`

### 內容製作
- **ArticleWorld** - 完整文章撰寫團隊
  - 連結：https://github.com/pin0513/ArticleWorld
  - 標籤：`writing`, `content`, `article`

### 簡報製作
- **SlidesWorld** - 專業簡報製作團隊
  - 連結：https://github.com/pin0513/SlidesWorld
  - 標籤：`presentation`, `slides`, `design`

- **PowerPointExpert** - PowerPoint 操作專家
  - 連結：https://github.com/pin0513/PowerPointExpert
  - 標籤：`powerpoint`, `presentation`

### 管理教練
- **DeptManagerCoach** - 部門主管教練
  - 連結：https://github.com/pin0513/DeptManagerCoach
  - 標籤：`management`, `leadership`, `coach`

---

## 3️⃣ 工具性 Skills（2 個）

**優先級**: ⭐⭐⭐ (中)
**install_type**: `global_link`
**自動更新**: ✅

### AI 工具整合
- **AITools** - AI 相關工具整合
  - 連結：https://github.com/pin0513/AITools
  - 標籤：`ai`, `tools`, `integration`

### DevOps 工具整合
- **DevOpsTools** - Jira、Azure DevOps、GitHub、Teams 整合
  - 連結：https://github.com/pin0513/DevOpsTools
  - 功能：
    - ✅ Jira 整合
    - ✅ Azure DevOps 整合
    - ✅ GitHub 操作
    - ✅ Microsoft Teams 通知
  - 標籤：`devops`, `jira`, `azure`, `github`, `teams`

---

## 4️⃣ 專業團隊 (Agent Teams)（2 個）

**優先級**: ⭐⭐ (一般)
**install_type**: `project`（安裝到 `~/AgentProjects/`）
**自動更新**: ❌（因為可能有客製化修改）

### 全端開發團隊
- **fullstack-react-dotnet** - React + .NET 全端開發團隊
  - 連結：https://github.com/pin0513/fullstack-react-dotnet
  - 來源：A-Team
  - 技術棧：
    - 前端：React, TypeScript
    - 後端：.NET Core, C#
    - 資料庫：SQL Server / PostgreSQL
  - 標籤：`fullstack`, `react`, `dotnet`, `development`

### App 開發團隊
- **app-team-v1** - App 互動開發團隊
  - 連結：https://github.com/pin0513/app-team-v1
  - 來源：A-Team
  - 支援平台：
    - ✅ iOS (Swift / SwiftUI)
    - ✅ Android (Kotlin / Jetpack Compose)
    - ✅ 跨平台 (React Native / Flutter)
  - 標籤：`app`, `mobile`, `ios`, `android`, `development`

---

## 📊 統計總覽

| 分類 | 數量 | 自動更新 | 安裝位置 |
|------|------|----------|----------|
| **Anthropic 官方** | 16 | ✅ | `~/.claude/skills/` |
| **官方核心專案** | 3 | 部分 | `~/.claude/skills/` / `~/AgentProjects/` |
| **專業級 Skills** | 5 | ✅ | `~/.claude/skills/` |
| **工具性 Skills** | 2 | ✅ | `~/.claude/skills/` |
| **專業團隊** | 2 | ❌ | `~/AgentProjects/` |
| **總計** | **28** | - | - |

---

## 🚀 使用方式

### 安裝官方 Skills/Teams

```bash
cd ~/AgentProjects/dopeman/dopeman-app/commands
./install-official.py
```

### 依類別安裝

```
選擇: 2) 安裝 Skills/Teams
選擇: 1) 依類別選擇
選擇類別：
  1 - Anthropic 官方 Skills (16 個)
  2 - DopeMAN 官方專案 (3 個)
  3 - 專業級 Skills (5 個)
  4 - 工具性 Skills (2 個)
  5 - 專業團隊 (2 個)
```

### 檢查更新

```bash
./install-official.py
選擇: 3) 檢查更新
```

---

## 📁 安裝位置

### Global Skills
```
~/.claude/skills/
├── docx/                      ← Anthropic
├── pdf/                       ← Anthropic
├── pptx/                      ← Anthropic
├── xlsx/                      ← Anthropic
├── mcp-builder/               ← Anthropic
├── skill-creator/             ← Anthropic
├── ... (其他 Anthropic skills)
├── dopeman/                   ← 官方核心
├── product-strategy-coach/    ← 專業級
├── article-world/             ← 專業級
├── slides-world/              ← 專業級
├── powerpoint-expert/         ← 專業級
├── dept-manager-coach/        ← 專業級
├── ai-tools/                  ← 工具性
└── devops-tools/              ← 工具性
```

### Project Teams
```
~/AgentProjects/
├── claude-punk/               ← 官方核心 Team
├── a-team/                    ← 官方核心 Team
├── fullstack-react-dotnet/    ← 專業團隊
└── app-team-v1/               ← 專業團隊
```

---

## 🔄 版本管理

### 自動更新項目 (✅)
- Anthropic 官方 Skills（16 個）
- 專業級 Skills（5 個）
- 工具性 Skills（2 個）
- DopeMAN（1 個）

### 手動更新項目 (❌)
- 專業團隊（2 個）- 可能有客製化修改
- CLAUDE-PUNK、A-Team - 可能有本地調整

---

## 📚 參考資源

**Anthropic 官方**：
- [Skills Repository](https://github.com/anthropics/skills)
- [Building Skills Guide](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)

**DopeMAN 專案**：
- [GitHub Repository](https://github.com/pin0513/dopeman)
- [Official Catalog](./dopeman-app/commands/official-catalog.json)
- [Install Script](./dopeman-app/commands/install-official.py)

---

**Last Updated**: 2026-02-10
**Catalog Version**: 1.1.0
**Total Skills/Teams**: 28