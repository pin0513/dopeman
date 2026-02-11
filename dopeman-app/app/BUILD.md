# DopeMAN App 打包指南

> 建立時間：2026-02-11
> 版本：v2.1.1

---

## 前置需求

### 系統需求

- **macOS**: 10.13+ (High Sierra 或更新)
- **Python**: 3.9+ (系統需已安裝)
- **Node.js**: 18+ (用於 Electron 打包)

### 安裝依賴

```bash
# 1. 進入 app 目錄
cd /Users/paul_huang/AgentProjects/dopeman/dopeman-app/app

# 2. 安裝 Node.js 依賴
npm install

# 3. 確保 Python 依賴已安裝（在 commands/ 目錄）
cd ../commands
pip3 install -r requirements.txt
```

---

## Python 環境說明

### 依賴策略

DopeMAN 使用 **系統 Python** 策略：
- ✅ 不打包 Python 解釋器（檔案較小）
- ✅ 使用使用者系統的 Python 3
- ⚠️ 需要使用者預先安裝 Python 依賴

### 依賴檢查

App 啟動時會自動檢查：
- Python 3 是否可用
- 必要套件是否已安裝（flask, flask-cors, asyncio）

若檢查失敗，App 會顯示錯誤訊息並退出。

---

## 打包流程

### 快速打包

```bash
cd /Users/paul_huang/AgentProjects/dopeman/dopeman-app/app

# 打包 macOS .app 和 .dmg
npm run build:dmg
```

### 輸出位置

```
app/dist/
├── DopeMAN-2.1.1.dmg           ← DMG 安裝檔（可分發）
├── DopeMAN-2.1.1-arm64.dmg     ← Apple Silicon 專用
├── DopeMAN-2.1.1-x64.dmg       ← Intel 專用
└── mac/
    └── DopeMAN.app             ← macOS App（可直接執行）
```

---

## 打包後結構

### .app 內部結構

```
DopeMAN.app/
├── Contents/
│   ├── MacOS/
│   │   └── DopeMAN                       ← 執行檔
│   ├── Resources/
│   │   ├── app.asar                      ← Electron App（壓縮）
│   │   ├── commands/                     ← Python 後端（未壓縮）
│   │   │   ├── api-server.py
│   │   │   ├── websocket-server.py
│   │   │   ├── control-center-real.html
│   │   │   ├── css/
│   │   │   ├── js/
│   │   │   └── requirements.txt
│   │   └── icon.icns
│   ├── Info.plist
│   └── PkgInfo
```

### 為什麼 commands/ 在 Resources/ 外？

- **原因**：Python 腳本需要未壓縮的純文字格式才能執行
- **設計**：使用 `extraResources` 配置將 commands/ 放在 Resources/ 根目錄
- **好處**：後端獨立於 app.asar，可讀寫、可修改、可調試

---

## 啟動流程

### App 啟動時發生的事

```
1. [Electron] main.js 啟動
   ↓
2. [Process Manager] 檢查 Python 環境
   ↓
3. [Process Manager] 啟動 api-server.py (port 8891)
   ↓
4. [Process Manager] 啟動 websocket-server.py (port 8892)
   ↓
5. [Electron] 等待 2 秒（確保伺服器啟動）
   ↓
6. [Electron] 開啟 BrowserWindow 載入 http://127.0.0.1:8891/control-center-real.html
   ↓
7. [Dashboard] 顯示 Skills Control Center
```

### App 關閉時發生的事

```
1. [Electron] 接收到 before-quit 事件
   ↓
2. [Process Manager] 停止 api-server.py (SIGTERM)
   ↓
3. [Process Manager] 停止 websocket-server.py (SIGTERM)
   ↓
4. [Electron] App 退出
```

---

## 測試打包結果

### 測試 .app

```bash
# 1. 直接執行
open app/dist/mac/DopeMAN.app

# 2. 檢查 Console 輸出
# 開啟 Console.app（系統內建）
# 搜尋 "DopeMAN" 查看日誌
```

### 測試 .dmg

```bash
# 1. 掛載 DMG
open app/dist/DopeMAN-2.1.1.dmg

# 2. 拖曳到 Applications 安裝

# 3. 開啟
open /Applications/DopeMAN.app
```

### 驗證清單

- [ ] App 成功啟動，無錯誤訊息
- [ ] Console 顯示 HTTP Server 和 WebSocket Server 啟動訊息
- [ ] BrowserWindow 載入 Dashboard 正常
- [ ] Dashboard 顯示 Skills 資料（讀取 control-center-real-data.json）
- [ ] Tab 切換功能正常
- [ ] 樹狀圖展開/收合正常
- [ ] 操作按鈕可點擊
- [ ] 關閉 App 後，Python 伺服器也停止（檢查 `ps aux | grep python`）

---

## 常見問題

### Q1: 打包後檔案很大（> 500MB）

**A**: 正常。包含：
- Electron 框架（~150MB）
- commands/ 完整內容（~10-50MB）
- node_modules/（若未排除，可能 > 100MB）

**優化**：在 `package.json` 的 `build.files` 中排除不必要的 node_modules。

### Q2: 打包後無法啟動，提示 Python 錯誤

**A**: 檢查：
1. 使用者系統是否安裝 Python 3
2. 是否執行 `pip3 install -r requirements.txt`
3. 查看 Console.app 日誌，確認錯誤訊息

### Q3: Dashboard 顯示空白頁

**A**: 可能原因：
1. HTTP Server 未啟動（檢查 port 8891 是否被佔用）
2. 路徑問題（檢查 `control-center-real.html` 是否在 commands/）
3. 等待時間不足（調整 main.js 的 `setTimeout` 延遲）

### Q4: 如何調試打包後的 App？

**A**:
```bash
# 1. 開啟 DevTools（在 main.js 中啟用）
# 2. 查看 Console.app 日誌
# 3. 手動啟動 Python 腳本測試：
cd /Applications/DopeMAN.app/Contents/Resources/commands
python3 api-server.py
```

### Q5: 能否打包成 Windows 或 Linux 版本？

**A**: 可以，修改 `package.json` 的 `build.win` 或 `build.linux` 配置。
但需要在對應平台上執行打包（或使用 CI/CD）。

---

## 檔案大小預估

| 項目 | 大小 |
|------|------|
| Electron 框架 | ~150MB |
| commands/ 目錄 | ~30MB |
| 壓縮前總大小 | ~180MB |
| DMG 壓縮後 | ~120-150MB |

---

## 相關文件

- **package.json**: Electron 打包配置
- **electron/main.js**: App 主程序
- **electron/process-manager.js**: Python 服務管理
- **electron/preload.js**: 渲染進程預加載
- **commands/requirements.txt**: Python 依賴清單

---

## 更新打包版本

```bash
# 1. 修改版本號
nano app/package.json  # 修改 "version": "2.1.2"

# 2. 重新打包
npm run build:dmg

# 3. 輸出
ls -lh app/dist/DopeMAN-2.1.2.dmg
```

---

**版本**: v2.1.1
**建立日期**: 2026-02-11
**維護者**: web-produce-frontend
**狀態**: ✅ 打包配置完成，等待測試
