# Anthropic 官方 Skills 整合說明

## 🎯 新增功能

DopeMAN 現已整合 **Anthropic 官方 16 個 Skills**，可一鍵自動安裝！

## 📦 包含的 Skills

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

## 🚀 使用方式

### 啟動安裝器

```bash
cd ~/AgentProjects/dopeman/dopeman-app/commands
./install-official.py
```

### 安裝 Anthropic Skills

```
選擇: 2) 安裝 Skills/Teams
選擇: 1) 依類別選擇
選擇: 1  → Anthropic 官方 Skills
```

系統會自動：
1. 使用 sparse-checkout 下載特定 skill（不下載整個 repo）
2. 安裝到 `~/.claude/skills/{skill-id}/`
3. 自動建立 commands 連結（如果有）
4. 更新 skills registry

---

## 📁 安裝位置

```
~/.claude/skills/
├── docx/
├── pdf/
├── pptx/
├── xlsx/
├── mcp-builder/
└── ... (其他 skills)
```

---

## 🔄 自動更新

所有 Anthropic 官方 skills 預設啟用自動更新：

```bash
./install-official.py
選擇: 3) 檢查更新
```

---

## 📚 技術細節

### Sparse Checkout 支援

安裝腳本支援從單一 repo 安裝特定子目錄：

```python
# install-official.py 新增功能
if 'subpath' in item:
    # 使用 sparse-checkout 只下載 skills/docx/
    git init
    git remote add origin https://github.com/anthropics/skills
    git config core.sparseCheckout true
    echo "skills/docx/*" > .git/info/sparse-checkout
    git pull origin main
```

### Catalog 結構

```json
{
  "categories": {
    "anthropic": {
      "name": "Anthropic 官方 Skills",
      "priority": 1,
      "items": [
        {
          "id": "docx",
          "repo": "https://github.com/anthropics/skills",
          "subpath": "skills/docx",  ← 關鍵：指定子目錄
          "install_type": "global_link",
          "auto_update": true
        }
      ]
    }
  }
}
```

---

## 🔗 相關資源

- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [官方安裝指南](./commands/INSTALL-OFFICIAL-GUIDE.md)
- [Official Catalog](./commands/official-catalog.json)
- [Install Script](./commands/install-official.py)

---

**Version**: 1.1.0 | **Date**: 2026-02-10
