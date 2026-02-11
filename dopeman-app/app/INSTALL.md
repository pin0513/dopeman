# DopeMAN App 安裝與測試指南

> 快速安裝與測試步驟

---

## 安裝依賴

### 1. Node.js 依賴

```bash
cd /Users/paul_huang/AgentProjects/dopeman/dopeman-app/app
npm install
```

**預期輸出**：
```
added 200+ packages in 15s
```

### 2. Python 依賴

```bash
cd /Users/paul_huang/AgentProjects/dopeman/dopeman-app/commands
pip3 install -r requirements.txt
```

**預期輸出**：
```
Successfully installed flask-3.0.0 flask-cors-4.0.0 ...
```

---

## 開發測試

### 啟動開發模式

```bash
cd /Users/paul_huang/AgentProjects/dopeman/dopeman-app/app
npm start
```

**預期行為**：
1. Console 顯示 `[DopeMAN] App is ready`
2. Console 顯示 `[HTTP Server] Running on port 8891`
3. Console 顯示 `[WebSocket Server] Running on port 8892`
4. 自動開啟 Electron 視窗
5. 視窗載入 Dashboard (http://127.0.0.1:8891/control-center-real.html)
6. Dashboard 正常顯示，資料正常載入

**如果失敗**：
- 檢查 port 8891, 8892 是否被佔用
- 檢查 Python 依賴是否完整安裝
- 查看 Console.app 日誌

---

## 打包測試

### 打包成 .dmg

```bash
cd /Users/paul_huang/AgentProjects/dopeman/dopeman-app/app
npm run build:dmg
```

**打包過程**：
```
⨯ electron-builder  version=24.9.1 os=darwin
⨯ building         target=macOS DM output=/Users/paul_huang/AgentProjects/dopeman/dopeman-app/app/dist
⨯ packaging        arch=x64 file=dist/mac/DopeMAN.app
⨯ packaging        arch=arm64 file=dist/mac-arm64/DopeMAN.app
⨯ building block map  blockMapFile=dist/DopeMAN-2.1.1-arm64.dmg.blockmap
⨯ building         target=DM arch=x64 file=dist/DopeMAN-2.1.1.dmg
✓ Build complete   time=45s
```

**輸出檔案**：
```
app/dist/
├── DopeMAN-2.1.1.dmg           (~120-150MB)
├── DopeMAN-2.1.1-arm64.dmg     (~120-150MB)
└── mac/
    └── DopeMAN.app             (~180MB 未壓縮)
```

### 測試 .app

```bash
# 直接執行
open app/dist/mac/DopeMAN.app

# 檢查是否正常啟動
ps aux | grep DopeMAN
ps aux | grep python  # 應該看到 api-server.py 和 websocket-server.py
```

### 測試 .dmg

```bash
# 掛載 DMG
open app/dist/DopeMAN-2.1.1.dmg

# 手動拖曳到 Applications 安裝
# 或使用指令
cp -R "/Volumes/DopeMAN 2.1.1/DopeMAN.app" /Applications/

# 啟動已安裝的版本
open /Applications/DopeMAN.app
```

---

## 驗證清單

### 開發模式驗證

- [ ] `npm start` 成功啟動
- [ ] Console 無錯誤訊息
- [ ] HTTP Server 在 port 8891 啟動
- [ ] WebSocket Server 在 port 8892 啟動
- [ ] Electron 視窗開啟
- [ ] Dashboard 載入成功
- [ ] 資料正常顯示（Skills, Agents, Rules）
- [ ] Tab 切換功能正常
- [ ] 關閉視窗後 Python 服務停止

### 打包版本驗證

- [ ] `npm run build:dmg` 成功完成
- [ ] dist/ 目錄包含 .dmg 和 .app
- [ ] .app 可直接執行
- [ ] .dmg 可正常掛載
- [ ] 從 .dmg 安裝到 Applications 成功
- [ ] 已安裝的 App 可正常啟動
- [ ] 打包版本功能與開發版本一致
- [ ] 關閉 App 後 Python 服務停止

---

## Icon 更新（可選）

目前使用佔位 icon（`build/icon-placeholder.svg`）。

**如需自定義 icon**：
1. 準備 1024x1024 PNG 圖片
2. 使用工具轉換為 .icns（macOS）
3. 放置到 `app/build/icon.icns`
4. 更新 `package.json` 的 `build.mac.icon` 路徑
5. 重新打包

**推薦工具**：
- [IconKit](https://github.com/codefu09/IconKit) - 免費 icon 轉換工具
- [iconutil](https://developer.apple.com/library/archive/documentation/GraphicsAnimation/Conceptual/HighResolutionOSX/Optimizing/Optimizing.html) - macOS 內建

---

## 常見問題

### Q: npm install 失敗

**A**: 檢查 Node.js 版本：
```bash
node --version  # 應該 >= 18
npm --version   # 應該 >= 9
```

### Q: Python 依賴安裝失敗

**A**: 使用虛擬環境：
```bash
cd /Users/paul_huang/AgentProjects/dopeman/dopeman-app/commands
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### Q: 打包後 App 無法啟動

**A**: 查看 Console.app 日誌：
1. 開啟 Console.app
2. 搜尋 "DopeMAN"
3. 查看錯誤訊息
4. 常見問題：Python 依賴未安裝

### Q: Dashboard 顯示空白

**A**: 檢查：
```bash
# 確認 HTML 檔案存在
ls -la app/dist/mac/DopeMAN.app/Contents/Resources/commands/control-center-real.html

# 確認 Python 服務啟動
ps aux | grep api-server
ps aux | grep websocket-server

# 檢查 port 是否被佔用
lsof -i :8891
lsof -i :8892
```

---

## 下一步

✅ 安裝與測試完成後：
1. 將 .dmg 分發給使用者
2. 使用者只需雙擊 .dmg 安裝
3. 確保使用者系統已安裝 Python 3 和依賴

📋 相關文件：
- **[BUILD.md](./BUILD.md)** - 詳細打包指南
- **[README.md](./README.md)** - 專案說明

---

**版本**: v2.1.1
**建立日期**: 2026-02-11
**狀態**: ✅ 配置完成，可開始測試
