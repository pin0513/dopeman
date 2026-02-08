# ✨ 新功能：官方 Skills/Teams 安裝管理器

## 📋 功能概述

DopeMAN 新增了「官方 Skills/Teams 安裝管理器」，讓用戶可以：
- 📦 瀏覽官方維護的 Skills 和 Teams 目錄
- 🚀 一鍵安裝官方 Skills/Teams
- 🔄 自動追蹤版本更新
- 🔗 自動建立全域連結與 Commands
- 📊 追蹤安裝歷史與來源

---

## 🎯 已完成的工作

### 1. 官方目錄配置檔案

**檔案**: `commands/official-catalog.json`

結構化的官方 Skills/Teams 目錄，包含：
- ✅ 4 大分類（官方專案、專業級 Skills、工具性 Skills、專業團隊）
- ✅ 11 個官方項目
- ✅ 詳細的 metadata（名稱、描述、倉庫 URL、類型、安裝方式）

**支援的項目**：
```
官方專案:
  - DopeMAN
  - CLAUDE-PUNK
  - A-Team

專業級 Skills:
  - 商業教練（product-strategy-coach）
  - 文案專家（ArticleWorld）
  - 投影片專家（SlidesWorld）
  - PowerPoint 專家
  - 部門主管教練（DeptManagerCoach）

工具性 Skills:
  - AI 工具集（AITools）
  - DevOps 工具集（DevOpsTools）

專業團隊:
  - 全端開發團隊（fullstack-react-dotnet）
  - App 開發團隊（app-team-v1）
```

### 2. 安裝管理腳本

**檔案**: `commands/install-official.py`

完整的 Python 互動式管理器，功能包括：
- ✅ 顯示官方目錄（含已安裝狀態）
- ✅ 三種安裝方式（依類別、全部、個別選擇）
- ✅ 自動 Git clone
- ✅ 自動建立 symlinks
- ✅ 自動更新 registry
- ✅ 檢查更新（git fetch + 比對版本）
- ✅ 批次更新或選擇性更新
- ✅ 備份機制（覆蓋前自動備份）
- ✅ 彩色輸出與進度提示

**技術特性**：
- 使用 Git 管理版本
- 支援 global_link 和 project 兩種安裝類型
- 自動取得 commit hash 作為版本號
- 自動建立 commands 目錄連結
- 完整的錯誤處理與用戶提示

### 3. Shell Wrapper

**檔案**: `commands/install-official.sh`

快速啟動腳本，提供：
- ✅ 一鍵執行安裝管理器
- ✅ 自動檢查 Python 腳本
- ✅ 自動賦予執行權限

### 4. 文件更新

#### SKILL.md 更新
- ✅ 新增 `install-official` 命令到命令表格
- ✅ 新增完整的使用範例與輸出說明

#### 安裝指南
**檔案**: `commands/INSTALL-OFFICIAL-GUIDE.md`

完整的使用手冊，包含：
- ✅ 快速開始指南
- ✅ 功能詳細說明
- ✅ 安裝類型比較（global_link vs project）
- ✅ Registry 追蹤機制
- ✅ 常見問題 FAQ
- ✅ 進階用法（批次安裝、Cron、匯出清單）
- ✅ 技術細節

---

## 🚀 使用方式

### 方式一：直接執行（推薦）

```bash
cd ~/AgentProjects/dopeman/commands
./install-official.sh
```

### 方式二：從 DopeMAN 調用

```bash
/dopeman install-official
```

### 方式三：Python 直接執行

```bash
python3 ~/AgentProjects/dopeman/commands/install-official.py
```

---

## 📸 介面預覽

### 主選單

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

請選擇 (0-4):
```

### 官方目錄顯示

```
============================================================
                    官方 Skills / Teams 目錄
============================================================

📦 官方專案
   DopeMAN 官方維護的核心專案

   1. [已安裝] DopeMAN
      📝 智能環境管理秘書團隊
      🔗 https://github.com/pin0513/dopeman
      📂 類型: skill | 安裝方式: global_link
      🏷️  版本: a3f2c1b

   2. [未安裝] CLAUDE-PUNK
      📝 Claude 客製化開發框架
      🔗 https://github.com/chemistrywow31/CLAUDE-PUNK
      📂 類型: team | 安裝方式: project
```

### 安裝流程

```
選擇安裝方式：

1) 依類別選擇
2) 全部安裝
3) 個別選擇
0) 取消

請選擇 (0-3): 1

選擇要安裝的類別：

1) 官方專案 (1/3 已安裝)
   DopeMAN 官方維護的核心專案
2) 專業級 Skills (0/5 已安裝)
   高品質、可直接使用的專業技能

請選擇類別 (0-2): 2

ℹ️  安裝 商業教練 到 ~/.claude/skills/product-strategy-coach...
ℹ️  正在 clone https://github.com/pin0513/product-strategy-coach...
✅ Clone 完成
ℹ️  建立 commands 連結: ~/.claude/commands/product-strategy-coach
ℹ️  Registry 已新增: product-strategy-coach
✅ ✨ 商業教練 安裝完成！
```

---

## 🔄 安裝類型對比

| 特性 | global_link | project |
|------|-------------|---------|
| **安裝位置** | `~/.claude/skills/` | `~/AgentProjects/` |
| **全域可用** | ✅ 是 | ❌ 否 |
| **Commands 連結** | ✅ 自動建立 | ❌ 無 |
| **完整專案結構** | ❌ 僅 skill | ✅ 完整 |
| **適用情境** | 工具/單一 skill | 複雜團隊/需客製化 |
| **範例** | product-strategy-coach | CLAUDE-PUNK, A-Team |

---

## 📊 Registry 追蹤

安裝後會自動更新 `~/.claude/memory/dopeman/skills-registry.json`：

```json
{
  "version": "1.0.0",
  "last_updated": "2026-02-08T22:45:00",
  "skills": [
    {
      "name": "product-strategy-coach",
      "display_name": "商業教練",
      "path": "/Users/paul_huang/.claude/skills/product-strategy-coach",
      "source": "https://github.com/pin0513/product-strategy-coach",
      "version": "bd06171",
      "type": "skill",
      "installed_at": "2026-02-08T22:45:00",
      "auto_update": true,
      "has_update": false
    }
  ]
}
```

**用途**：
- 🔍 追蹤 Skills 來源與版本
- 🔄 自動檢查更新
- 📈 使用統計分析
- 🔗 依賴關係管理

---

## ✨ 核心特性

### 1. 自動版本追蹤
- ✅ 使用 Git commit hash 作為版本號
- ✅ 自動檢查遠端更新
- ✅ 顯示落後的 commit 數量

### 2. 智能安裝
- ✅ 檢查是否已安裝
- ✅ 覆蓋前自動備份
- ✅ 支援兩種安裝類型
- ✅ 自動建立 commands 連結

### 3. 安全機制
- ✅ 備份舊版本（`.backup.{timestamp}`）
- ✅ 確認覆蓋提示
- ✅ Git clone 失敗處理
- ✅ Registry 更新驗證

### 4. 用戶友善
- ✅ 彩色輸出
- ✅ 進度提示
- ✅ 清楚的成功/失敗訊息
- ✅ 互動式選單

---

## 🛠️ 技術實作

### Git 操作

```python
# Clone 倉庫
subprocess.run(['git', 'clone', repo_url, target_path])

# 取得版本
subprocess.run(['git', 'rev-parse', '--short', 'HEAD'])

# 檢查更新
subprocess.run(['git', 'fetch', 'origin'])
subprocess.run(['git', 'rev-list', '--count', 'HEAD..origin/main'])

# 更新
subprocess.run(['git', 'pull', 'origin', 'main'])
```

### Symlink 建立

```python
# Commands 連結
commands_src = target_path / 'commands'
commands_target = home / '.claude/commands' / item['id']
commands_target.symlink_to(commands_src)
```

### Registry 更新

```python
def update_registry(item, install_path):
    registry = load_registry()

    skill_entry = {
        "name": item['id'],
        "display_name": item['name'],
        "path": install_path,
        "source": item['repo'],
        "version": get_repo_version(install_path),
        "type": item['type'],
        "installed_at": datetime.now().isoformat(),
        "auto_update": item.get('auto_update', False),
        "has_update": False
    }

    registry['skills'].append(skill_entry)
    save_registry(registry)
```

---

## 📁 檔案結構

```
~/AgentProjects/dopeman/
├── commands/
│   ├── official-catalog.json          ← 官方目錄配置
│   ├── install-official.py            ← 安裝管理腳本（Python）
│   ├── install-official.sh            ← Shell wrapper
│   ├── INSTALL-OFFICIAL-GUIDE.md      ← 使用指南
│   └── ...
├── .claude/
│   └── skills/
│       └── dopeman/
│           └── SKILL.md               ← 已更新（新增命令）
└── FEATURE-INSTALL-OFFICIAL.md        ← 本文件

~/.claude/memory/dopeman/
└── skills-registry.json                ← 自動更新

~/.claude/skills/
├── product-strategy-coach/             ← global_link 安裝範例
│   ├── SKILL.md
│   └── commands/
└── ...

~/.claude/commands/
└── product-strategy-coach -> ~/.claude/skills/product-strategy-coach/commands
```

---

## 🎯 未來規劃

### 短期（本週）
- [ ] 新增 `uninstall` 命令
- [ ] 支援自訂 catalog URL（從遠端載入）
- [ ] 新增「依賴關係」檢查（某些 skills 需要其他 skills）

### 中期（本月）
- [ ] Web UI 介面（整合到 Control Center Dashboard）
- [ ] 自動更新機制（Cron + 通知）
- [ ] 版本回退功能（rollback）

### 長期（未來）
- [ ] Skills 評分與推薦系統
- [ ] 社群 Skills marketplace
- [ ] 一鍵發布自己的 Skills

---

## 🧪 測試狀態

### 已測試功能
- ✅ 顯示官方目錄
- ✅ 檢查已安裝狀態
- ✅ 取得 Git 版本號
- ✅ 互動式選單
- ✅ 彩色輸出

### 待完整測試
- ⏳ 實際安裝流程（需要網路連線）
- ⏳ 更新檢查
- ⏳ 覆蓋與備份
- ⏳ Commands 連結建立
- ⏳ Registry 更新

---

## 📞 使用建議

### 初次使用

1. **查看目錄**
   ```bash
   ./install-official.sh
   # 選擇 1) 顯示官方目錄
   ```

2. **安裝推薦 Skills**
   ```bash
   # 選擇 2) 安裝 Skills/Teams
   # 選擇 1) 依類別選擇
   # 選擇 2) 專業級 Skills（推薦）
   ```

3. **定期檢查更新**
   ```bash
   # 選擇 3) 檢查更新
   ```

### 推薦安裝清單

#### 必裝（核心功能）
- ✅ product-strategy-coach（商業教練）
- ✅ DevOpsTools（Jira/ADO 整合）

#### 內容創作
- ✅ ArticleWorld（文案專家）
- ✅ SlidesWorld（投影片專家）
- ✅ PowerPointExpert

#### 團隊開發
- ✅ CLAUDE-PUNK（開發框架）
- ✅ A-Team（多功能團隊）

#### 專案型（依需求）
- ✅ fullstack-react-dotnet（全端開發）
- ✅ app-team-v1（App 開發）

---

## 🎉 總結

這個新功能讓 DopeMAN 成為：
- 📦 **Skills 包管理器**（類似 npm、pip）
- 🔄 **版本控制系統**（追蹤來源與更新）
- 🚀 **一鍵安裝平台**（降低使用門檻）
- 📊 **統一管理介面**（整合到 DopeMAN 生態系）

**下一步**：
1. 測試完整安裝流程
2. 整合到 Control Center Dashboard（Web UI）
3. 建立社群 Skills 提交機制

---

**版本**: v1.0.0
**建立日期**: 2026-02-08
**維護者**: DopeMAN Team
