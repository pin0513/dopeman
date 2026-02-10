# DopeMAN - 官方 Skills/Teams 安裝指南

## 快速開始

### 方式一：互動式介面（推薦）

```bash
cd ~/AgentProjects/dopeman/commands
./install-official.sh
```

### 方式二：從 DopeMAN 技能調用

```bash
/dopeman install-official
```

---

## 功能說明

### 1. 顯示官方目錄

查看所有可安裝的官方 Skills/Teams，包括：
- 官方專案（DopeMAN、CLAUDE-PUNK、A-Team）
- 專業級 Skills（商業教練、文案專家、投影片專家、部門主管教練）
- 工具性 Skills（AI 工具集、DevOps 工具集）
- 專業團隊（全端開發、App 開發）

每個項目顯示：
- ✅ [已安裝] 或 ⚠️ [未安裝]
- 名稱與描述
- GitHub 倉庫 URL
- 類型（skill / team）
- 安裝方式（global_link / project）
- 版本號（若已安裝）

### 2. 安裝 Skills/Teams

三種安裝方式：

#### 依類別選擇
選擇一個類別，安裝該類別下所有未安裝的項目。

**範例**：選擇「專業級 Skills」會安裝：
- 商業教練（product-strategy-coach）
- 文案專家（ArticleWorld）
- 投影片專家（SlidesWorld）
- PowerPoint 專家
- 部門主管教練

#### 全部安裝
一次安裝所有官方 Skills/Teams。

**注意**：會下載約 ~500MB 資料，需輸入 `yes` 確認。

#### 個別選擇
從列表中選擇特定項目安裝。

**範例**：
```
請輸入編號 (例如: 1 3 5): 2 4 7
```

### 3. 檢查更新

檢查已安裝的官方 Skills/Teams 是否有新版本。

自動執行：
1. `git fetch origin` 取得最新資訊
2. 比對本地與遠端版本
3. 顯示有多少個 commit 落後

更新選項：
- 全部更新
- 選擇性更新（逐個確認）
- 略過

### 4. 查看已安裝清單

顯示目前已安裝的官方 Skills/Teams，包括：
- 安裝路徑
- 版本號（Git commit hash）

---

## 安裝類型

### global_link（全域連結）

**特性**：
- 安裝到 `~/.claude/skills/{id}`
- 全域可用（任何目錄都可呼叫）
- 自動建立 commands 連結（若存在）

**適用於**：
- 獨立的 skills（如 product-strategy-coach）
- 工具性 skills（如 DevOpsTools）

**範例**：
```bash
~/.claude/skills/product-strategy-coach/
  ├── SKILL.md
  ├── commands/
  └── ...

~/.claude/commands/product-strategy-coach -> ~/.claude/skills/product-strategy-coach/commands
```

### project（專案型）

**特性**：
- 安裝到 `~/AgentProjects/{id}`
- 完整專案結構（含 Git、.claude/、CLAUDE.md）
- 不建立全域連結

**適用於**：
- 複雜團隊（如 CLAUDE-PUNK、A-Team）
- 需要客製化的專案（如 fullstack-react-dotnet）

**範例**：
```bash
~/AgentProjects/CLAUDE-PUNK/
  ├── CLAUDE.md
  ├── .claude/
  │   ├── agents/
  │   ├── skills/
  │   └── rules/
  └── ...
```

---

## Registry 追蹤

安裝後會自動更新 `~/.claude/memory/dopeman/skills-registry.json`：

```json
{
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
- 追蹤 Skills 來源
- 版本管理
- 更新檢查
- 依賴分析

---

## 常見問題

### Q1: 如何更新已安裝的 Skills？

**A**: 使用「檢查更新」功能：
```bash
./install-official.sh
# 選擇 3) 檢查更新
```

### Q2: 安裝時遇到衝突怎麼辦？

**A**: 腳本會提示是否覆蓋，並自動備份現有版本到：
```
{skill-name}.backup.20260208_224500
```

### Q3: 如何卸載某個 Skill？

**A**: 手動刪除目錄並清理 registry：
```bash
# 刪除 skill
rm -rf ~/.claude/skills/product-strategy-coach

# 刪除 commands 連結（若存在）
rm -f ~/.claude/commands/product-strategy-coach

# 手動編輯 registry.json 移除對應條目
```

**未來功能**：將提供 `uninstall` 命令。

### Q4: global_link 和 project 的差異？

| 比較項目 | global_link | project |
|---------|-------------|---------|
| 安裝位置 | `~/.claude/skills/` | `~/AgentProjects/` |
| 全域可用 | ✅ 是 | ❌ 否 |
| Commands | ✅ 自動連結 | ❌ 無 |
| 完整專案 | ❌ 僅 skill | ✅ 完整結構 |
| 適用情境 | 工具/單一 skill | 複雜團隊/需客製化 |

### Q5: 如何新增自己的 Skills 到目錄？

**A**: 編輯 `commands/official-catalog.json`：

```json
{
  "categories": {
    "custom": {
      "name": "我的自訂 Skills",
      "description": "個人開發的 Skills",
      "priority": 5,
      "items": [
        {
          "id": "my-awesome-skill",
          "name": "我的超讚 Skill",
          "repo": "https://github.com/yourname/my-awesome-skill",
          "type": "skill",
          "description": "做超讚的事情",
          "install_type": "global_link",
          "auto_update": true
        }
      ]
    }
  }
}
```

---

## 進階用法

### 批次安裝特定 Skills

```bash
# 安裝所有專業級 Skills
echo -e "2\n1\n2\n0" | ./install-official.sh
```

### 定期檢查更新（Cron）

```bash
# 每天早上 9:00 檢查更新
0 9 * * * cd ~/AgentProjects/dopeman/commands && echo "3" | ./install-official.sh > /tmp/dopeman-update.log 2>&1
```

### 匯出已安裝清單

```bash
python3 -c "
import json
from pathlib import Path

registry = Path.home() / '.claude/memory/dopeman/skills-registry.json'
data = json.loads(registry.read_text())

print('已安裝的官方 Skills/Teams:')
for skill in data['skills']:
    if 'github.com/pin0513' in skill['source'] or 'github.com/chemistrywow31' in skill['source']:
        print(f'  - {skill[\"display_name\"]} ({skill[\"version\"]})')
"
```

---

## 技術細節

### 安裝流程

1. **驗證**：檢查目標位置是否已存在
2. **備份**：若存在，備份舊版本
3. **Clone**：`git clone {repo} {target_path}`
4. **連結**：建立 commands symlink（若為 global_link）
5. **註冊**：更新 skills-registry.json
6. **驗證**：取得 commit hash 確認安裝成功

### 更新檢查流程

1. **Fetch**：`git fetch origin`
2. **比較**：`git rev-list --count HEAD..origin/main`
3. **顯示**：列出落後的 commit 數量
4. **更新**：`git pull origin main`（若用戶確認）

### Registry 結構

- `name`: Skill ID（用於路徑與識別）
- `display_name`: 顯示名稱（中文）
- `path`: 實際安裝路徑
- `source`: GitHub 倉庫 URL
- `version`: Git commit hash（短版本）
- `type`: skill / team
- `installed_at`: 安裝時間（ISO 8601）
- `auto_update`: 是否自動更新
- `has_update`: 是否有新版本

---

**版本**: v1.0.0
**建立日期**: 2026-02-08
**維護者**: DopeMAN Team
