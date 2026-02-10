# DopeMAN Desktop App

DopeMAN 智能環境管理秘書的獨立桌面應用程式版本。

## ✨ 特色功能

- ✅ **獨立安裝** - 雙擊執行，無需額外安裝 Python
- ✅ **單一實例** - 自動防止重複開啟
- ✅ **自動端口偵測** - 每次啟動自動尋找可用端口（8891-8999）
- ✅ **系統托盤** - 最小化到系統托盤，不佔用工作區
- ✅ **跨平台** - 支援 macOS、Windows、Linux

---

## 📦 安裝

### macOS

1. 下載 `DopeMAN-1.0.0.dmg`
2. 雙擊打開 DMG 檔案
3. 拖曳 DopeMAN.app 到 Applications 資料夾
4. 第一次執行可能需要在「安全性與隱私權」中允許

### Windows

1. 下載 `DopeMAN-Setup-1.0.0.exe`
2. 雙擊執行安裝程式
3. 按照安裝精靈指示操作
4. 完成後可在開始選單找到 DopeMAN

### Linux

1. 下載 `DopeMAN-1.0.0.AppImage`
2. 給予執行權限：`chmod +x DopeMAN-1.0.0.AppImage`
3. 雙擊執行或命令列執行：`./DopeMAN-1.0.0.AppImage`

---

## 🚀 使用方式

### 啟動應用程式

- **macOS**: 在 Launchpad 或 Applications 資料夾中點擊 DopeMAN
- **Windows**: 從開始選單或桌面捷徑啟動
- **Linux**: 執行 AppImage 檔案

### 系統托盤功能

應用程式啟動後會在系統托盤顯示圖示，右鍵點擊可以：

- 📊 **開啟 Dashboard** - 顯示 Skills Control Center
- 🎛️ **任務監控** - 開啟任務監控頁面
- 🔍 **重新掃描** - 觸發 Skills 掃描
- 🏥 **健康檢查** - 執行環境健康檢查
- ℹ️ **端口資訊** - 查看當前使用的端口
- ❌ **結束** - 完全關閉應用程式

### 自動端口偵測

應用程式會自動在 8891-8999 範圍內尋找可用端口：

- HTTP Server: 第一個可用端口（例如 8891）
- WebSocket Server: 下一個可用端口（例如 8892）

如果預設端口被佔用，會自動切換到其他可用端口，無需手動設定。

---

## 🔧 開發模式

### 環境需求

- Node.js 18+
- Python 3.8+
- npm 或 yarn

### 安裝依賴

```bash
cd dopeman-app
npm install
```

### 開發執行

```bash
# 啟動開發模式（含 DevTools）
npm run dev

# 一般啟動
npm start
```

### 打包應用程式

```bash
# 打包當前平台
npm run build

# 打包 macOS
npm run build:mac

# 打包 Windows
npm run build:win

# 打包所有平台
npm run build:all
```

產出檔案位於 `dist/` 目錄。

---

## 📂 專案結構

```
dopeman-app/
├── package.json          # Node.js 專案配置
├── src/
│   ├── main.js           # Electron 主程序
│   ├── preload.js        # 預載腳本
│   ├── port-detector.js  # 端口偵測模組
│   └── python-server.js  # Python 伺服器管理
├── commands/             # Python 後端腳本
│   ├── control-center-real.html
│   ├── task-monitor.html
│   ├── websocket-server.py
│   ├── scan-real-data.py
│   └── health-check.py
├── assets/               # 圖示與資源
│   ├── icon.png          # App 圖示
│   ├── icon.icns         # macOS 圖示
│   ├── icon.ico          # Windows 圖示
│   └── tray-icon.png     # 托盤圖示
└── dist/                 # 打包產出目錄
```

---

## 🛠️ 技術架構

### Electron Shell

- **主程序** (main.js): 管理應用程式生命週期、視窗、托盤
- **預載腳本** (preload.js): 暴露安全 API 給前端
- **端口偵測** (port-detector.js): 自動尋找可用端口
- **伺服器管理** (python-server.js): 管理 Python 子進程

### Python Backend

- **HTTP Server**: 提供靜態檔案（Dashboard、Task Monitor）
- **WebSocket Server**: 即時任務進度監控
- **掃描腳本**: 掃描 Skills/Agents/Projects
- **健康檢查**: 環境健康檢查與診斷

### 前端介面

- **Control Center**: Skills 總覽與管理
- **Task Monitor**: 即時任務監控與執行

---

## 🔒 安全性

### Context Isolation

使用 Electron 的 Context Isolation 確保前端無法直接存取 Node.js API。

### Preload Script

透過 `contextBridge` 暴露有限且安全的 API：

```javascript
window.dopeman.getPorts()      // 取得端口資訊
window.dopeman.scanSkills()    // 觸發掃描
window.dopeman.healthCheck()   // 健康檢查
```

### 單一實例鎖定

確保同時只有一個應用程式實例運行，避免端口衝突。

---

## 📊 效能考量

### 記憶體使用

- Electron 基礎：~80-100 MB
- Python 伺服器：~20-30 MB
- 總計：約 100-130 MB

### 啟動時間

- 首次啟動：~2-3 秒（含端口偵測、Python 啟動）
- 後續啟動：~1-2 秒

### 打包大小

- macOS .dmg: ~150-200 MB
- Windows .exe: ~180-220 MB
- Linux .AppImage: ~150-180 MB

---

## ❓ 常見問題

### Q: 為什麼第一次啟動較慢？

A: 首次啟動需要：
1. 偵測可用端口
2. 啟動 Python HTTP Server
3. 啟動 WebSocket Server
4. 載入 Dashboard 介面

後續啟動會更快。

### Q: 如何更改預設端口範圍？

A: 編輯 `src/main.js` 中的端口範圍：

```javascript
httpPort = await findAvailablePort(8891, 8999); // 修改此範圍
```

### Q: 可以同時執行多個實例嗎？

A: 不行。應用程式使用單一實例鎖定，嘗試開啟第二個實例時會聚焦到現有視窗。

### Q: 如何完全關閉應用程式？

A: 右鍵點擊托盤圖示 → 選擇「結束」，或在 Dashboard 視窗使用 Cmd+Q (macOS) / Alt+F4 (Windows)。

### Q: 資料儲存在哪裡？

A: 應用程式使用以下位置：
- **macOS**: `~/Library/Application Support/DopeMAN/`
- **Windows**: `%APPDATA%/DopeMAN/`
- **Linux**: `~/.config/DopeMAN/`

---

## 🐛 故障排除

### 應用程式無法啟動

1. 檢查 Python 3 是否已安裝：`python3 --version`
2. 檢查端口 8891-8999 是否被佔用
3. 查看日誌檔案（位於應用程式資料目錄）

### 端口被佔用

應用程式會自動尋找可用端口。如果所有端口都被佔用：

1. 關閉其他佔用端口的程式
2. 或修改 `src/main.js` 中的端口範圍

### Dashboard 無法載入

1. 檢查 HTTP Server 是否正常啟動（查看托盤選單的端口資訊）
2. 嘗試重新啟動應用程式
3. 檢查防火牆是否阻擋 localhost 連線

---

## 📝 更新日誌

### v1.0.0 (2026-02-10)

- 🎉 初始版本
- ✅ 獨立安裝與執行
- ✅ 單一實例鎖定
- ✅ 自動端口偵測
- ✅ 系統托盤支援
- ✅ 跨平台打包（macOS/Windows/Linux）

---

## 📄 授權

MIT License

---

## 🙏 致謝

- Electron - 跨平台桌面應用框架
- Python - 後端伺服器與腳本
- DopeMAN Team - 原始專案開發

---

**需要協助？** 請查看 [GitHub Issues](https://github.com/pin0513/dopeman/issues)
