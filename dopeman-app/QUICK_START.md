# DopeMAN App - 快速開始指南

## 📦 Phase 1: 基礎執行（現在可用）

### 1. 安裝依賴

```bash
cd /Users/paul_huang/AgentProjects/dopeman/dopeman-app
npm install
```

### 2. 測試執行

```bash
# 開發模式（會開啟 DevTools）
npm run dev

# 一般模式
npm start
```

### 3. 驗證功能

應用程式啟動後：
- ✅ 檢查是否只有一個實例
- ✅ 查看托盤圖示是否顯示
- ✅ 確認 Dashboard 正常載入
- ✅ 測試任務監控功能

### 4. 測試單一實例

```bash
# 開啟第一個實例
npm start

# 在另一個終端機嘗試開啟第二個
npm start
# → 應該會聚焦到第一個視窗而非開啟新視窗
```

---

## 🎨 圖示轉換（需要手動執行）

### macOS 圖示 (.icns)

需要使用 `iconutil` 工具（macOS 內建）：

```bash
cd assets

# 1. 建立 iconset 目錄
mkdir icon.iconset

# 2. 生成各種尺寸（需要手動或使用 sips）
sips -z 16 16     icon-1024.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon-1024.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon-1024.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon-1024.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon-1024.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon-1024.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon-1024.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon-1024.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon-1024.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon-1024.png --out icon.iconset/icon_512x512@2x.png

# 3. 轉換為 .icns
iconutil -c icns icon.iconset

# 4. 清理
rm -rf icon.iconset
```

### Windows 圖示 (.ico)

需要使用 `png2ico` 或線上工具：

```bash
# 使用 ImageMagick
convert icon-1024.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico

# 或使用線上工具
# https://convertico.com/
# https://icoconvert.com/
```

### 簡化版本（使用腳本）

```bash
# 執行圖示轉換腳本
./scripts/convert-icons.sh
```

---

## 🔧 Phase 2: 開發與測試

### 修改端口範圍

編輯 `src/main.js`:

```javascript
// 預設: 8891-8999
httpPort = await findAvailablePort(8891, 8999);

// 自訂範圍
httpPort = await findAvailablePort(9000, 9100);
```

### 修改視窗大小

編輯 `src/main.js`:

```javascript
mainWindow = new BrowserWindow({
  width: 1600,    // 修改寬度
  height: 1000,   // 修改高度
  // ...
});
```

### 測試托盤功能

1. 啟動應用程式
2. 最小化視窗（不是關閉）
3. 點擊托盤圖示應該會顯示選單
4. 測試各項功能：
   - 開啟 Dashboard
   - 任務監控
   - 重新掃描
   - 健康檢查

---

## 📦 Phase 3: 打包測試

### 安裝打包工具

```bash
npm install --save-dev electron-builder
```

### 打包當前平台

```bash
# macOS
npm run build:mac

# Windows (需在 Windows 上執行)
npm run build:win

# 或兩者都打包（macOS 上可以打包 Windows）
npm run build:all
```

### 驗證打包結果

```bash
# 檢查產出檔案
ls -lh dist/

# macOS
open dist/DopeMAN-1.0.0.dmg

# Windows
# 複製 dist/DopeMAN-Setup-1.0.0.exe 到 Windows 機器測試
```

---

## 🐛 常見問題

### Q: npm install 失敗

```bash
# 清除快取重試
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Q: Python 找不到

確認 Python 3 已安裝：

```bash
which python3
python3 --version
```

### Q: 端口被佔用

```bash
# 查看佔用端口的程式
lsof -i :8891
lsof -i :8892

# 關閉佔用的程式
kill -9 <PID>
```

### Q: 圖示未顯示

1. 檢查 `assets/icon.png` 是否存在
2. 重新啟動應用程式
3. 清除 Electron 快取：`rm -rf ~/Library/Application\ Support/DopeMAN/`

---

## 📋 檢查清單

### 開發階段
- [ ] npm install 成功
- [ ] npm start 可以執行
- [ ] Dashboard 正常顯示
- [ ] WebSocket 連線成功
- [ ] 托盤圖示顯示
- [ ] 單一實例鎖定運作
- [ ] 端口自動偵測運作

### 打包階段
- [ ] 圖示轉換完成（.icns, .ico）
- [ ] npm run build 成功
- [ ] DMG 可以安裝（macOS）
- [ ] EXE 可以安裝（Windows）
- [ ] 安裝後可以執行
- [ ] 功能完整運作

---

## 🚀 下一步

完成 Phase 1-3 後，可以進行：

1. **UX 優化** - 啟動畫面、設定頁面
2. **自動更新** - 整合 electron-updater
3. **效能優化** - Python 打包為可執行檔
4. **發布** - 上傳到 GitHub Releases

---

**需要協助？** 請查看詳細的 [README.md](./README.md)
