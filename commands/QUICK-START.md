# DopeMAN Control Center - 快速開始

## ⚡ 5 秒啟動

```bash
cd /Users/paul_huang/AgentProjects/dopeman/commands
./start-control-center.sh
```

然後開啟瀏覽器：**http://localhost:8891/control-center-real.html**

---

## ✅ 修正確認

### ✅ 問題已修正

**之前的問題**：
- 點擊「重新 Scan」→ ❌ 只重新讀取 JSON，不執行掃描

**修正後**：
- 點擊「重新 Scan」→ ✅ 執行 Python 掃描 → 更新 JSON → 重新載入

### ✅ 測試結果

```bash
$ curl -X POST http://localhost:8891/api/rescan
{
  "success": true,
  "message": "掃描完成"
}
```

---

## 🛠️ 常用操作

### 啟動伺服器

```bash
./start-control-center.sh
```

### 停止伺服器

```bash
pkill -f control-center-server
```

### 僅執行掃描（不啟動伺服器）

```bash
python3 scan-real-data.py
```

### 測試 API

```bash
./test-api.sh
```

---

## 📋 檢查清單

啟動前請確認：

- [ ] Python 3 已安裝
- [ ] 端口 8891 未被占用
- [ ] 檔案權限正確（已執行 `chmod +x *.sh`）

---

## 🐛 快速疑難排解

### 問題：點擊「重新 Scan」沒有反應

**檢查伺服器是否運行**：
```bash
lsof -i :8891
```

**如果沒有輸出**：
```bash
./start-control-center.sh
```

### 問題：掃描失敗

**查看錯誤訊息**：
```bash
python3 scan-real-data.py
```

### 問題：端口被占用

**停止舊的伺服器**：
```bash
pkill -f control-center-server
lsof -i :8891  # 確認端口已釋放
./start-control-center.sh  # 重新啟動
```

---

## 📁 相關檔案

| 檔案 | 說明 |
|------|------|
| `start-control-center.sh` | 一鍵啟動腳本 |
| `control-center-server.py` | HTTP 伺服器 |
| `scan-real-data.py` | 掃描腳本 |
| `control-center-real.html` | Dashboard 前端 |
| `CONTROL-CENTER-README.md` | 完整文件 |

---

**修正版本**：2.0.0
**測試日期**：2026-02-09
**狀態**：✅ API 正常運行
