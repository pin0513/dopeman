# DopeMAN Desktop App

**智能環境管理秘書團隊 - 獨立桌面應用程式**

---

## 快速開始

### 安裝依賴

```bash
# 1. 安裝 Node.js 依賴
npm install

# 2. 安裝 Python 依賴（在 commands/ 目錄）
cd ../commands
pip3 install -r requirements.txt
cd ../app
```

### 開發模式

```bash
# 啟動 Electron App（開發模式）
npm start
```

### 打包應用程式

```bash
# 打包成 .dmg 安裝檔
npm run build:dmg

# 輸出位置
ls -lh dist/DopeMAN-*.dmg
```

---

## 專案結構

```
app/
├── electron/                      ← Electron 主程序
│   ├── main.js                    ← App 進入點
│   ├── process-manager.js         ← Python 服務管理
│   └── preload.js                 ← 渲染進程預加載
├── build/                         ← 打包資源
│   └── icon.png                   ← App 圖示（待新增）
├── package.json                   ← Node.js 配置
├── BUILD.md                       ← 詳細打包指南
└── README.md                      ← 本檔案
```

---

## 技術架構

### Frontend
- **Electron**: 桌面應用框架
- **HTML/CSS/JS**: Dashboard 介面（來自 commands/）

### Backend
- **Python 3**: HTTP API Server (port 8891)
- **Python 3**: WebSocket Server (port 8892)
- **Flask**: Web 框架

### 打包策略
- **Electron**: 打包在 app.asar
- **Python 後端**: 放在 Resources/commands/（未壓縮）
- **依賴**: 使用系統 Python + pip 安裝依賴

---

## 詳細文件

完整打包流程、測試方法、常見問題請參考：
- **[BUILD.md](./BUILD.md)** - 完整打包指南

---

## 版本資訊

- **版本**: v2.1.1
- **建立日期**: 2026-02-11
- **維護者**: web-produce-frontend

---

## 相關專案

- **DopeMAN Skill**: `~/.claude/skills/dopeman/`
- **Commands**: `../commands/`
- **專案文件**: `../CLAUDE.md`
