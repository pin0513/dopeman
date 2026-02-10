# 個人資訊匯流功能 - 使用說明

## 已實作功能 ✅

### 1. PTT 熱門文章爬蟲

**資料來源**：PTT 八卦板（Gossiping）
**更新頻率**：手動觸發
**資料內容**：
- 前10名熱門文章
- 標題、推文數、作者、日期
- 直接連結到 PTT 文章

**狀態**：✅ 已完成（真實爬取）

### 2. 台股資料

**資料來源**：yfinance (Yahoo Finance API)
**資料內容**：
- 漲幅排行前30名
- 跌幅排行前30名
- 重要指數（加權指數）
- 從 50 檔熱門台股中取樣

**狀態**：✅ 已完成（真實資料，使用 yfinance）

---

## 使用方式

### 方法 1：自動化更新腳本（推薦）

```bash
# 一鍵更新所有資料（Skills + 個人資訊匯流）
cd ~/AgentProjects/dopeman/commands
./update-all-data.sh
```

### 方法 2：單獨執行爬蟲

```bash
# 只更新 PTT + 台股資料（推薦使用 v2）
cd ~/AgentProjects/dopeman/commands
python3 fetch-ptt-stocks-v2.py

# 或使用舊版（已不建議）
# python3 fetch-ptt-stocks.py
```

### 方法 3：透過網頁介面

1. 開啟 Control Center v2: http://localhost:8891/control-center-v2.html
2. 點擊右上角「🔄 更新資料」按鈕
3. 手動執行命令後重新載入頁面

---

## 檔案說明

| 檔案 | 說明 |
|------|------|
| `fetch-ptt-stocks-v2.py` | PTT + 台股爬蟲主程式（v2，使用 yfinance） |
| `fetch-ptt-stocks.py` | PTT + 台股爬蟲（v1，舊版，使用 HTML 解析） |
| `info-stream-data.json` | 爬取的資料（JSON 格式） |
| `update-all-data.sh` | 自動化更新腳本（已更新為使用 v2） |
| `control-center-v2.html` | 新版 Dashboard（含資訊匯流 Tab） |

---

## 資料結構

### info-stream-data.json

```json
{
  "metadata": {
    "generated_at": "2026-02-10T00:00:00",
    "version": "1.0.0"
  },
  "social": {
    "ptt": {
      "gossiping": {
        "trending": [
          {
            "title": "[問卦] 文章標題",
            "board": "Gossiping",
            "push_count": 100,
            "author": "作者",
            "date": "2/10",
            "url": "https://www.ptt.cc/..."
          }
        ]
      }
    }
  },
  "stocks": {
    "tw": {
      "top_gainers": [
        {
          "symbol": "2330",
          "name": "台積電",
          "price": 580.0,
          "change": 18.0,
          "change_percent": 3.2,
          "volume": "45,234張",
          "type": "stock"
        }
      ],
      "top_losers": [...],
      "indices": {...}
    }
  }
}
```

---

## 待實作功能 ⚠️

以下功能已預留 UI 介面，但需要進一步開發：

### 預測市場

- [ ] Polymarket API 整合
- [ ] Kalshi API 整合
- [ ] Manifold Markets API 整合

**需要**：API Keys + 爬蟲實作

### 美股資料

- [ ] Yahoo Finance US Stock 爬蟲
- [ ] S&P 500 指數
- [ ] 漲跌排行榜

**需要**：調整爬蟲 URL 與選擇器

### 其他社群平台

- [ ] Threads API（需要 Meta API Key）
- [ ] YouTube API（需要 Google API Key）
- [ ] Instagram API（需要 Meta API Key）
- [ ] X (Twitter) API（需要 X API Key）

**需要**：各平台 API Keys

### 熱門內容

- [ ] 書籍排行榜（Amazon Best Sellers / Goodreads）
- [ ] 商品排行榜（Amazon / PChome）
- [ ] 音樂排行榜（Spotify / Apple Music）

**需要**：爬蟲實作或 API 整合

---

## 已知問題與限制

### 1. PTT 爬蟲

**問題**：PTT 可能有頻率限制，過於頻繁請求會被暫時封鎖
**解決方案**：
- 已加入延遲機制（每次請求間隔2秒）
- 加入完整的 User-Agent headers
- 如果被擋，會自動使用 Mock 資料

### 2. Yahoo Finance 台股

**問題**：Yahoo Finance 的 HTML 結構經常變更
**目前狀態**：使用 Mock 資料
**解決方案**：
1. 改用 Yahoo Finance API（需要 API key）
2. 或改用 TWSE（台灣證券交易所）公開資料
3. 或使用第三方金融 API（如 Alpha Vantage）

### 3. 資料更新頻率

**目前**：手動觸發更新
**建議**：可設定定時任務（cron job）自動更新

```bash
# 範例：每小時更新一次
# crontab -e
0 * * * * cd ~/AgentProjects/dopeman/commands && ./update-all-data.sh
```

---

## 擴展建議

### 短期（1-2週內可完成）

1. **改善台股爬蟲**
   - 使用 TWSE 公開資料 API
   - 或使用 yfinance Python 套件

2. **加入美股資料**
   - Yahoo Finance US
   - 使用 yfinance 套件更可靠

3. **資料快取機制**
   - 避免過度爬取
   - 設定快取有效期（例如：15分鐘）

### 中期（1個月內）

1. **整合預測市場 API**
   - Polymarket
   - Manifold Markets（免費）

2. **整合 YouTube API**
   - 需要 Google Cloud API Key（免費額度）
   - 爬取熱門影片

3. **建立定時任務**
   - 自動更新機制
   - 錯誤通知

### 長期（未來規劃）

1. **即時更新**
   - WebSocket 推送
   - 自動刷新 UI

2. **個人化設定**
   - 選擇關注的資料源
   - 自訂更新頻率

3. **歷史資料追蹤**
   - 儲存歷史資料
   - 趨勢分析

---

## 技術細節

### Python 套件需求

```bash
pip3 install requests beautifulsoup4
```

### 爬蟲技術

- **requests**：HTTP 請求
- **BeautifulSoup4**：HTML 解析
- **Mock 資料**：當爬取失敗時的 fallback

### 前端技術

- **原生 JavaScript**：無依賴框架
- **Fetch API**：非同步載入資料
- **CSS Grid & Flexbox**：響應式佈局

---

## 疑難排解

### Q1: PTT 資料無法載入

**檢查**：
```bash
cd ~/AgentProjects/dopeman/commands
python3 fetch-ptt-stocks.py
```

如果顯示「Connection reset」，表示 PTT 暫時拒絕連線，會自動使用 Mock 資料。

### Q2: 台股資料都是 Mock 資料

**原因**：可能使用了舊版爬蟲（v1）

**解決方案**：

1. 使用 v2 版本（推薦）：
```bash
cd ~/AgentProjects/dopeman/commands
python3 fetch-ptt-stocks-v2.py
```

2. 確認已安裝 yfinance：
```bash
pip3 install yfinance
```

3. 檢查 `update-all-data.sh` 是否使用 v2 版本

### Q3: 網頁顯示「資料建置中」

**原因**：尚未執行爬蟲或 JSON 檔案不存在

**解決方案**：
```bash
cd ~/AgentProjects/dopeman/commands
python3 fetch-ptt-stocks.py
# 重新載入網頁
```

---

## 版本資訊

**版本**：v2.0.0
**日期**：2026-02-10
**作者**：DopeMAN Team

### 版本歷史

**v2.0.0** (2026-02-10)
- ✅ 台股爬蟲改用 yfinance（真實資料）
- ✅ 支援 50 檔熱門台股取樣
- ✅ 加權指數（^TWII）即時資料
- ✅ 自動化腳本更新為 v2
- ✅ 移除 Yahoo Finance HTML 解析依賴

**v1.0.0** (2026-02-10)
- ✅ PTT 爬蟲（真實資料）
- ⚠️ 台股爬蟲（Mock 資料）
- ✅ 自動化更新腳本
- ✅ 前端資料顯示
- ✅ 全新 v2 UI 設計
