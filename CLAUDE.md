# DopeMAN - 環境管理秘書團隊

## 團隊定位

DopeMAN 是一個智能環境管理團隊，專注於：
- **環境整理** - 自動分類目錄、識別專案狀態
- **Skills 生命週期管理** - 追蹤來源、檢測更新、管理繼承鏈
- **Skills 市場探索** - 發現熱門新 skills、評估品質、推薦引入
- **使用分析優化** - 統計習慣、識別冷門/過載、提供優化建議
- **跨電腦同步** - 匯出/匯入環境配置

---

## 部署模式

### Subagent 模式（預設）

DopeMAN 使用 **Subagent 模式**運作：
- **coordinator** 作為總調度者，負責任務分派與結果整合
- 所有 worker agents 透過 `Task` tool 被調用
- 適合順序性工作流程，清晰的交接關係

---

## 啟動方式

### 自動檢查（啟動時）

每次啟動 DopeMAN，自動執行：
```
🔍 自動檢查中...

✓ 掃描目錄              (file-organizer)
✓ 檢查 skills 更新      (skill-tracker)
✓ 搜尋新推薦            (skill-scout)
✓ 分析使用數據          (usage-analyst)

📢 結果通知：
   - 🔔 有 X 個 skills 可更新
   - 📂 有 Y 個專案待處理
   - 💡 推薦安裝 {skill-name}
   - ⚠️ {skill-name} 已 N 天未使用
```

### 手動觸發

```bash
/dopeman check-updates       # 檢查更新
/dopeman organize ~/DEV      # 整理目錄
/dopeman export-config       # 匯出配置
/dopeman import-config       # 匯入配置
/dopeman usage-report        # 使用報告
```

---

## 目錄結構管理

### 四類目錄分類

```
📁 產出區（Output）
   ├── slides/                    ← 簡報產出
   ├── AgentProjects/             ← Agent 團隊產出
   └── 部門資料與結果/             ← 報告、分析結果

📁 工作區（Work）
   ├── DEV/                       ← 正在開發的專案
   └── 部門資料-待整理/            ← 要處理的原始資料

📁 參考區（Reference）
   ├── skills-source/             ← 外部 skill repos
   └── skills-derived/            ← 基於別人 skill 改的

📁 暫存區（Temp）
   └── demo/試驗/練習/            ← 臨時性質的
```

### 自動分類規則

- **產出**：`/output/`, `/slides/`, `/reports/`, `*-report.json`
- **工作**：`/DEV/`, `/workspace/`, `.git` 存在的專案
- **參考**：`/skills/`, `/repos/`, `README*` 存在且無 `.git`
- **暫存**：`/tmp/`, `/demo/`, `*.tmp`, 最近 7 天未修改

---

## Skills Registry 結構

### 資料位置

```
~/.claude/memory/dopeman/
├── skills-registry.json         ← Skill 來源與版本記錄
├── skill-recommendations.json   ← 推薦的新 skills
├── usage-report.json            ← 使用統計報告
├── operation.log                ← 操作日誌
└── github-cache.json            ← GitHub API 快取
```

### Registry 格式

```json
{
  "skills": [
    {
      "name": "github-api-operations",
      "path": "~/.claude/skills/shared/github-api-operations",
      "source": "https://github.com/anthropics/claude-code",
      "version": "v1.2.3",
      "installed_at": "2026-02-07",
      "forked_from": null,
      "local_modifications": [],
      "used_by": ["skill-tracker", "skill-scout"],
      "last_used": "2026-02-07",
      "has_update": false
    },
    {
      "name": "my-custom-commit",
      "path": "~/.claude/skills/specialized/my-custom-commit",
      "source": "local",
      "version": "1.0.0",
      "installed_at": "2026-01-15",
      "forked_from": "https://github.com/user/repo/skills/commit",
      "local_modifications": ["added team notification"],
      "used_by": ["dev-team-pm"],
      "last_used": "2026-02-01",
      "has_update": true,
      "update_info": {
        "upstream_version": "1.1.0",
        "breaking_changes": false
      }
    }
  ]
}
```

---

## Skills 繼承鏈管理

### 追蹤機制

當你基於某個 skill 創建客製化版本時，DopeMAN 會記錄：
```
base-skill (upstream)
    ↓ forked_from
custom-skill (local)
    ↓ used_by
your-agent
```

### 更新通知

當 upstream skill 更新時，收到通知：
```
⚠️  檢測到更新：
   來源: github.com/user/repo/base-skill (v1.2.3 → v1.3.0)
   影響:
     - ~/.claude/skills/base-skill (v1.2.3)
     - ~/.claude/skills/custom-skill (基於 v1.2.3)
     - AgentProjects/my-team/team-skill (基於 v1.2.3)

   破壞性變更: 無
   建議動作: [查看 diff] [更新全域] [略過]
```

---

## Skills Market 探索

### 品質評分標準

| 指標 | 權重 | 說明 |
|------|------|------|
| Stars | 10% | GitHub stars > 100 加分 |
| 活躍度 | 30% | 最近 30 天有 commit |
| 文件 | 30% | 有 README、範例、changelog |
| 測試 | 20% | 有測試檔案 |
| 社群 | 10% | 有 issues/PR 互動 |

總分 ≥ 60 才會推薦。

### 推薦格式

```
💡 發現新 Skill：

playwright-helper (GitHub: 1.2k ⭐, Score: 78/100)
- 用途：簡化 Playwright E2E 測試腳本生成
- 相關：你的 automation-engineer agent
- 來源：github.com/user/playwright-helper
- 建議：可取代現有的手動測試腳本

原因：你最近 7 天執行了 15 次 E2E 測試，此 skill 可節省 60% 時間
```

---

## 使用分析與優化

### 統計維度

- **Skill 使用頻率**：每個 skill 被呼叫次數
- **Agent 執行時間**：每個 agent 的總執行時間
- **專案活躍度**：每個專案的最後修改時間
- **時間分配**：工作專案 vs 個人專案比例

### 優化建議類型

**移除建議**：
```
⚠️  old-skill-1 已 180 天未使用
   建議：移除或歸檔
   影響：無 agent 依賴此 skill
```

**拆分建議**：
```
⚠️  dev-team-lead agent 職責過多
   目前負責：任務分派、技術審查、進度追蹤、品質把關
   建議：拆分為 tech-lead（技術）+ project-coordinator（管理）
   預期效益：減少 40% 單一 agent 過載
```

**合併建議**：
```
💡 skill-a 和 skill-b 功能重疊 80%
   使用頻率：skill-a (2 次/週), skill-b (3 次/週)
   建議：合併為統一 skill
   預期效益：減少維護成本、避免選擇困難
```

---

## 專案與全域同步

### 雙版本架構

DopeMAN 同時存在於兩個位置：

**全域 Skill** (`~/.claude/skills/dopeman/`)：
- 用途：在任何目錄都可呼叫
- 內容：僅 `SKILL.md`
- 更新：從專案 push

**開發專案** (`~/DEV/projects/dopeman/`)：
- 用途：獨立開發、版本控制、功能擴展
- 內容：完整團隊結構（agents/skills/rules/commands）
- 更新：git 版本控制

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

**修改專案版本**：
```bash
cd ~/DEV/projects/dopeman
# 編輯 .claude/skills/dopeman/SKILL.md
git add .
git commit -m "feat: add new feature"
```

**推送到全域**：
```bash
./commands/sync-global-skill.sh
# 選擇 2) Push
```

**從全域更新**：
```bash
./commands/sync-global-skill.sh
# 選擇 1) Pull
```

**檢查同步狀態**：
```bash
./commands/sync-global-skill.sh
# 選擇 4) Status
```

### 安全機制

- ✅ Push 前自動備份全域版本
- ✅ 差異比較避免誤覆蓋
- ✅ 狀態檢查確保同步
- ✅ Git 版本控制可追蹤變更

---

## 跨電腦同步

### 匯出內容

```
dopeman-config.zip
├── skills-registry.json          ← Skill 清單與來源
├── skills-export/                ← 實際 skill 檔案
│   ├── shared/
│   └── specialized/
├── agents-export/                ← Agent 檔案
├── rules-export/                 ← Rule 檔案
├── directory-metadata.json       ← 目錄分類規則
├── usage-history.json            ← 使用統計（可選）
└── import.sh                     ← 自動匯入腳本
```

### 匯入流程

1. **備份現有配置**：`.backup/{timestamp}/`
2. **解壓配置包**：檢查完整性（checksum）
3. **執行匯入腳本**：
   - 安裝缺失的 skills
   - 恢復 registry 資料
   - 套用目錄分類規則
4. **產生差異報告**：列出新增/更新/衝突項目
5. **用戶確認**：處理衝突項目

---

## 團隊規則

所有 agents 必須遵守：

1. **no-silent-failures** - 所有錯誤必須記錄與通知
2. **backup-before-modify** - 修改資料前必須備份
3. **idempotent-operations** - 所有操作可重複執行
4. **log-all-actions** - 所有檔案操作與 API 呼叫必須記錄
5. **respect-rate-limits** - GitHub API 必須遵守 rate limit

---

## 快速參考

### 常用指令

```bash
# 檢查更新
/dopeman check-updates

# 整理目錄
/dopeman organize ~/DEV

# 匯出環境
/dopeman export --target=usb

# 使用報告
/dopeman usage-report --period=30days

# 推薦新 skills
/dopeman discover-skills
```

### Registry 查詢

```bash
# 列出所有 skills
cat ~/.claude/memory/dopeman/skills-registry.json | jq '.skills[].name'

# 檢查有更新的 skills
cat ~/.claude/memory/dopeman/skills-registry.json | jq '.skills[] | select(.has_update == true)'

# 查詢某個 skill 的來源
cat ~/.claude/memory/dopeman/skills-registry.json | jq '.skills[] | select(.name == "github-api-operations")'
```

---

## 關聯資源

- **Agent 檔案**：`.claude/agents/`
- **Skill 檔案**：`.claude/skills/`
- **Rule 檔案**：`.claude/rules/`
- **Memory 資料**：`~/.claude/memory/dopeman/`
- **操作日誌**：`~/.claude/memory/dopeman/operation.log`

---

**版本**：v1.0.0
**建立日期**：2026-02-07
**維護者**：DopeMAN Team
