# DopeMAN Commands

這個目錄包含 DopeMAN 團隊的常用指令腳本。

---

## 可用指令

### 1. 檢查更新
```bash
./check-updates.sh
```
檢查所有 skills 是否有新版本可用。

**功能**：
- 掃描 `~/.claude/skills/` 中的所有 skills
- 對比 GitHub upstream 的最新版本
- 顯示可更新清單與影響範圍
- 生成更新建議報告

---

### 2. 整理目錄
```bash
./organize-directory.sh [target-path]
```
自動分類指定目錄中的檔案。

**功能**：
- 掃描目標目錄（預設：`~/DEV`）
- 識別檔案類型與用途（產出/工作/參考/暫存）
- 提出移動/歸檔建議
- 用戶確認後執行操作

**範例**：
```bash
./organize-directory.sh ~/Documents/Slides  # 整理投影片目錄
./organize-directory.sh ~/DEV               # 整理開發目錄
```

---

### 3. 匯出配置
```bash
./export-config.sh [--target=usb|cloud|local] [--output=path]
```
匯出環境配置到指定位置。

**功能**：
- 打包 skills、agents、rules
- 匯出 registry 與 memory 資料
- 生成自動匯入腳本
- 計算 checksum 確保完整性

**範例**：
```bash
./export-config.sh --target=usb --output=/Volumes/USB/dopeman-backup.zip
./export-config.sh --target=local --output=~/Dropbox/
```

---

### 4. 匯入配置
```bash
./import-config.sh [config-path]
```
從配置包匯入環境設定。

**功能**：
- 備份現有配置到 `.backup/`
- 驗證配置包完整性（checksum）
- 解析路徑差異（跨平台相容）
- 處理版本衝突
- 生成差異報告

**範例**：
```bash
./import-config.sh ~/Downloads/dopeman-backup.zip
./import-config.sh /Volumes/USB/dopeman-backup.zip
```

---

### 5. 使用報告
```bash
./usage-report.sh [--period=7days|30days|90days]
```
生成 skills 與 agents 使用統計報告。

**功能**：
- 統計各 skill 的使用頻率
- 分析專案時間分配
- 識別冷門 skills（長期未使用）
- 識別過載 skills（使用過於頻繁）
- 提供優化建議

**範例**：
```bash
./usage-report.sh --period=30days   # 最近 30 天
./usage-report.sh --period=7days    # 最近 7 天
```

---

### 6. 探索新 Skills
```bash
./discover-skills.sh [--domain=testing|frontend|backend|all]
```
搜尋熱門新 skills 並推薦引入。

**功能**：
- 搜尋 GitHub 上的熱門 Claude skills
- 評估品質（stars、活躍度、文件、測試）
- 分析與現有 skills 的相關性
- 生成推薦清單與安裝指引

**範例**：
```bash
./discover-skills.sh --domain=testing    # 只搜尋測試相關
./discover-skills.sh --domain=all        # 搜尋所有領域
```

---

### 7. 初始化 Registry
```bash
./init-registry.sh
```
初始化 DopeMAN 的資料結構。

**功能**：
- 創建 `~/.claude/memory/dopeman/` 目錄
- 初始化 `skills-registry.json`
- 掃描現有 skills 並記錄
- 生成初始配置檔

**使用時機**：第一次使用 DopeMAN 時執行。

---

### 8. 驗證團隊結構
```bash
./validate-structure.sh
```
驗證 DopeMAN 團隊結構的完整性。

**功能**：
- 檢查所有 agents 檔案是否存在
- 驗證 skills 引用關係
- 檢查 YAML frontmatter 格式
- 驗證 rules 完整性
- 生成驗證報告

---

## 安裝

### 1. 設定執行權限
```bash
cd ~/teams/dopeman/commands
chmod +x *.sh
```

### 2. 加入 PATH（可選）
```bash
# 在 ~/.zshrc 或 ~/.bashrc 中加入
export PATH="$HOME/teams/dopeman/commands:$PATH"

# 重新載入
source ~/.zshrc
```

加入 PATH 後，可以直接執行：
```bash
check-updates.sh
organize-directory.sh ~/DEV
```

---

## 快速開始

### 第一次使用
```bash
# 1. 初始化 registry
./init-registry.sh

# 2. 掃描現有環境
./check-updates.sh

# 3. 查看使用報告
./usage-report.sh --period=30days
```

### 日常使用
```bash
# 每週檢查更新
./check-updates.sh

# 定期整理目錄
./organize-directory.sh ~/DEV

# 月底查看使用報告
./usage-report.sh --period=30days
```

### 換電腦時
```bash
# 舊電腦：匯出
./export-config.sh --target=usb --output=/Volumes/USB/backup.zip

# 新電腦：匯入
./import-config.sh /Volumes/USB/backup.zip
```

---

## 進階使用

### 自動化定期檢查

使用 cron 定期執行：
```bash
# 編輯 crontab
crontab -e

# 加入定期任務
0 9 * * 1 ~/teams/dopeman/commands/check-updates.sh  # 每週一早上 9 點
0 22 * * * ~/teams/dopeman/commands/organize-directory.sh ~/DEV  # 每天晚上 10 點
```

### 整合到 Git Hooks

在專案中加入 post-merge hook：
```bash
# .git/hooks/post-merge
#!/bin/bash
~/teams/dopeman/commands/check-updates.sh
```

---

## 疑難排解

### 問題 1：權限不足
```bash
# 解決方式：設定執行權限
chmod +x ~/teams/dopeman/commands/*.sh
```

### 問題 2：找不到 registry
```bash
# 解決方式：初始化 registry
./init-registry.sh
```

### 問題 3：GitHub API rate limit
```bash
# 解決方式：設定 GitHub token
export GITHUB_TOKEN="ghp_your_token_here"
```

---

## 相關文件

- **團隊說明**：`../CLAUDE.md`
- **Agents**：`../.claude/agents/`
- **Skills**：`../.claude/skills/`
- **Rules**：`../.claude/rules/`

---

**版本**：v1.0.0
**最後更新**：2026-02-07
