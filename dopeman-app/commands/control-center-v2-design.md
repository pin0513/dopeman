# DopeMAN Control Center v2.0 - 設計規格

## 設計理念

從「紫色漸層遊戲風」轉變為「專業深色系資訊中心」

### 色調系統

#### 主色調（Dark Theme）

```css
:root {
  /* 背景系統 */
  --bg-primary: #0f172a;        /* 深藍灰主背景 */
  --bg-secondary: #1e293b;      /* 次級背景 */
  --bg-tertiary: #334155;       /* 三級背景 */

  /* 表面（卡片、面板） */
  --surface-primary: #1e293b;   /* 主卡片 */
  --surface-hover: #334155;     /* hover 狀態 */
  --surface-active: #475569;    /* active 狀態 */

  /* 強調色 */
  --accent-primary: #3b82f6;    /* 藍色 - 主要操作 */
  --accent-success: #10b981;    /* 綠色 - 成功/正面 */
  --accent-warning: #f59e0b;    /* 橘色 - 警告 */
  --accent-danger: #ef4444;     /* 紅色 - 錯誤/危險 */
  --accent-info: #06b6d4;       /* 青色 - 資訊 */
  --accent-purple: #8b5cf6;     /* 紫色 - 特殊標記 */

  /* 文字系統 */
  --text-primary: #f1f5f9;      /* 主要文字 */
  --text-secondary: #cbd5e1;    /* 次要文字 */
  --text-muted: #94a3b8;        /* 弱化文字 */
  --text-disabled: #64748b;     /* 禁用文字 */

  /* 邊框 */
  --border-subtle: #334155;     /* 細微邊框 */
  --border-default: #475569;    /* 預設邊框 */
  --border-strong: #64748b;     /* 強調邊框 */

  /* 陰影 */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.3);

  /* 資料視覺化配色 */
  --chart-blue: #3b82f6;
  --chart-green: #10b981;
  --chart-orange: #f59e0b;
  --chart-red: #ef4444;
  --chart-purple: #8b5cf6;
  --chart-cyan: #06b6d4;
}
```

#### 漸層效果

```css
/* 標題漸層 */
.gradient-title {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* 卡片光暈效果 */
.card-glow {
  box-shadow:
    0 0 20px rgba(59, 130, 246, 0.1),
    0 4px 6px -1px rgba(0, 0, 0, 0.3);
}

/* 按鈕漸層 */
.btn-gradient {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
}
```

---

## 佈局架構

### 整體佈局

```
┌─────────────────────────────────────────────────────────────────┐
│  Header (固定頂部)                                               │
│  - Logo + 標題                                                   │
│  - 更新按鈕（右上角）                                            │
│  - 最後更新時間                                                  │
├─────────────────────────────────────────────────────────────────┤
│  Dashboard (統計卡片區 - 4 columns)                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Skills   │ │ Agents   │ │ Projects │ │ Commands │          │
│  │   154    │ │    59    │ │    10    │ │   106    │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
├─────────────────────────────────────────────────────────────────┤
│  Tab Navigation                                                 │
│  [ Skills ] [ Agents ] [ Projects ] [ 個人資訊匯流 🆕 ]          │
├─────────────────────────────────────────────────────────────────┤
│  Tab Content (可切換)                                           │
│                                                                 │
│  (根據選擇的 Tab 顯示對應內容)                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 個人資訊匯流 Tab 佈局

```
┌─────────────────────────────────────────────────────────────────┐
│  【個人資訊匯流】                                                │
│                                                                 │
│  ┌─ 預測市場 ──────────────────────────────────────────────┐   │
│  │ [Polymarket] [Kalshi] [Manifold Markets]                │   │
│  │                                                          │   │
│  │  Top 50 Events:                                         │   │
│  │  1. 2024 US Election Winner - Trump: 65% / Harris: 35% │   │
│  │  2. AI達到AGI時間 - 2025: 15% / 2026: 30% / ...        │   │
│  │  ...                                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─ 股市資訊 ──────────────────────────────────────────────┐   │
│  │ [台股] [美股]                                            │   │
│  │                                                          │   │
│  │  漲幅前30名:                                             │   │
│  │  1. 2330 台積電  ↑ +3.5%  📊 ETF: 0050, 006208          │   │
│  │  2. 2454 聯發科  ↑ +2.8%  📊 半導體類                   │   │
│  │  ...                                                     │   │
│  │                                                          │   │
│  │  重要指標:                                               │   │
│  │  加權指數: 18,520 (+1.2%)  |  S&P 500: 4,850 (+0.8%)   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─ 社群熱門 ──────────────────────────────────────────────┐   │
│  │ [PTT] [Threads] [YouTube] [Instagram] [X]               │   │
│  │                                                          │   │
│  │  PTT 今日熱門 Top 10:                                    │   │
│  │  1. [爆卦] xxxxx (八卦板) 🔥 1.2k推                     │   │
│  │  2. [問卦] yyyyy (八卦板) 💬 850推                      │   │
│  │  ...                                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─ 熱門內容 (可擴充) ──────────────────────────────────────┐   │
│  │ [書籍] [商品] [音樂]                                     │   │
│  │                                                          │   │
│  │  暢銷書籍:                                               │   │
│  │  1. Atomic Habits - James Clear                         │   │
│  │  2. ...                                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 組件設計

### 1. Header 設計

```css
.header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-subtle);
  padding: 1.5rem 2rem;
  backdrop-filter: blur(10px);
}

.header-content {
  max-width: 1600px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-subtitle {
  font-size: 1rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

.update-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.last-update {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.update-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
}

.update-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
}

.update-btn:active {
  transform: translateY(0);
}

.update-btn.loading .update-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

### 2. 統計卡片設計

```css
.stat-card {
  background: var(--surface-primary);
  border-radius: 1rem;
  padding: 1.5rem;
  border: 1px solid var(--border-subtle);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.stat-icon {
  font-size: 2rem;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-title {
  font-size: 0.875rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

.stat-value {
  font-size: 3rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-top: 0.5rem;
}
```

### 3. Tab Navigation 設計

```css
.tab-navigation {
  background: var(--surface-primary);
  border-bottom: 1px solid var(--border-subtle);
  padding: 0 2rem;
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
}

.tab {
  padding: 1rem 1.5rem;
  color: var(--text-secondary);
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.2s ease;
  font-weight: 500;
  white-space: nowrap;
  position: relative;
}

.tab:hover {
  color: var(--text-primary);
  background: var(--surface-hover);
}

.tab.active {
  color: var(--accent-primary);
  border-bottom-color: var(--accent-primary);
  background: var(--surface-hover);
}

.tab-badge {
  display: inline-block;
  background: var(--accent-danger);
  color: white;
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  border-radius: 9999px;
  margin-left: 0.5rem;
  font-weight: 700;
}
```

### 4. 資訊卡片設計（個人資訊匯流用）

```css
.info-section {
  background: var(--surface-primary);
  border-radius: 1rem;
  border: 1px solid var(--border-subtle);
  margin-bottom: 1.5rem;
  overflow: hidden;
}

.info-header {
  padding: 1.25rem 1.5rem;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.info-title-icon {
  font-size: 1.5rem;
}

.info-tabs {
  display: flex;
  gap: 0.5rem;
}

.info-tab {
  padding: 0.5rem 1rem;
  background: var(--surface-primary);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  font-weight: 500;
}

.info-tab:hover {
  background: var(--surface-hover);
  color: var(--text-primary);
}

.info-tab.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: white;
}

.info-body {
  padding: 1.5rem;
  max-height: 600px;
  overflow-y: auto;
}

/* 列表項目樣式 */
.info-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  padding: 1rem;
  background: var(--bg-secondary);
  border-radius: 0.5rem;
  border: 1px solid var(--border-subtle);
  transition: all 0.2s ease;
}

.info-item:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-md);
}

.info-item-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 0.5rem;
}

.info-item-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 1rem;
}

.info-item-meta {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.info-item-content {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* 漲跌顯示 */
.stock-change {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 600;
  font-size: 0.875rem;
}

.stock-change.up {
  background: rgba(16, 185, 129, 0.1);
  color: var(--accent-success);
}

.stock-change.down {
  background: rgba(239, 68, 68, 0.1);
  color: var(--accent-danger);
}

/* 熱度指標 */
.trend-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.trend-fire {
  color: var(--accent-danger);
}

.trend-count {
  font-weight: 600;
}
```

---

## 資料結構設計

### 個人資訊匯流資料格式

```json
{
  "prediction_markets": {
    "polymarket": {
      "events": [
        {
          "id": "xxx",
          "title": "2024 US Election Winner",
          "outcomes": [
            { "name": "Trump", "probability": 0.65 },
            { "name": "Harris", "probability": 0.35 }
          ],
          "volume": "$50M",
          "updated_at": "2026-02-09T16:00:00Z"
        }
      ]
    },
    "kalshi": { ... },
    "manifold": { ... }
  },
  "stocks": {
    "tw": {
      "top_gainers": [
        {
          "symbol": "2330",
          "name": "台積電",
          "change_percent": 3.5,
          "price": 580,
          "volume": "50,000張",
          "related_etfs": ["0050", "006208"]
        }
      ],
      "top_losers": [ ... ],
      "indices": {
        "taiex": { "value": 18520, "change": 1.2 }
      }
    },
    "us": { ... }
  },
  "social": {
    "ptt": {
      "trending": [
        {
          "title": "[爆卦] xxxxx",
          "board": "八卦板",
          "push_count": 1200,
          "url": "https://..."
        }
      ]
    },
    "threads": { ... },
    "youtube": { ... },
    "instagram": { ... },
    "x": { ... }
  },
  "trending_content": {
    "books": [ ... ],
    "products": [ ... ],
    "music": [ ... ]
  }
}
```

---

## 更新機制設計

### 更新按鈕功能

```javascript
async function updateAllData() {
  const updateBtn = document.querySelector('.update-btn');
  updateBtn.classList.add('loading');
  updateBtn.disabled = true;

  try {
    // 1. 掃描 Skills/Agents (原有功能)
    await fetch('/api/scan');

    // 2. 爬取個人資訊匯流資料 (新增)
    await fetch('/api/fetch-info-stream', {
      method: 'POST',
      body: JSON.stringify({
        sources: [
          'prediction_markets',
          'stocks',
          'social',
          'trending_content'
        ]
      })
    });

    // 3. 更新 UI
    location.reload();

  } catch (error) {
    console.error('更新失敗:', error);
    alert('更新失敗，請檢查網路連線');
  } finally {
    updateBtn.classList.remove('loading');
    updateBtn.disabled = false;
  }
}
```

### 後端 API 設計

```python
# commands/fetch-info-stream.py

import asyncio
import aiohttp
from datetime import datetime

async def fetch_prediction_markets():
    """爬取預測市場資料"""
    # Polymarket API
    # Kalshi API
    # Manifold Markets API
    pass

async def fetch_stock_data():
    """爬取股市資料"""
    # Yahoo Finance API (美股)
    # TWSE API (台股)
    pass

async def fetch_social_trends():
    """爬取社群熱門"""
    # PTT API
    # Threads/Instagram Graph API
    # YouTube Data API
    # X (Twitter) API
    pass

async def fetch_trending_content():
    """爬取熱門內容"""
    # Books: Amazon Best Sellers / Goodreads
    # Products: Amazon / PChome
    # Music: Spotify / Apple Music
    pass

async def main():
    results = await asyncio.gather(
        fetch_prediction_markets(),
        fetch_stock_data(),
        fetch_social_trends(),
        fetch_trending_content()
    )

    # 儲存到 JSON
    with open('info-stream-data.json', 'w') as f:
        json.dump({
            'prediction_markets': results[0],
            'stocks': results[1],
            'social': results[2],
            'trending_content': results[3],
            'updated_at': datetime.now().isoformat()
        }, f)
```

---

## 響應式設計

### 斷點設計

```css
/* Desktop First */
@media (max-width: 1280px) {
  /* 平板橫向 */
  .dashboard {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  /* 平板直立 */
  .dashboard {
    grid-template-columns: 1fr;
  }

  .header-content {
    flex-direction: column;
    gap: 1rem;
  }

  .tab-navigation {
    overflow-x: scroll;
  }
}

@media (max-width: 640px) {
  /* 手機 */
  .stat-value {
    font-size: 2rem;
  }

  .info-body {
    padding: 1rem;
  }
}
```

---

## 實作優先順序

### Phase 1: 基礎重設計（優先）
1. ✅ 更新色調系統（深色主題）
2. ✅ 重新設計 Header
3. ✅ 重新設計統計卡片
4. ✅ 更新 Tab Navigation 樣式

### Phase 2: 個人資訊匯流（次要）
1. ✅ 新增「個人資訊匯流」Tab
2. ✅ 設計資訊卡片組件
3. ⚠️ 實作後端爬蟲（需要 API keys）
4. ⚠️ 整合前端顯示

### Phase 3: 資料整合（延後）
1. ⚠️ 實作各資料源爬蟲
2. ⚠️ 快取機制
3. ⚠️ 錯誤處理與 fallback

---

## 交付說明

### 給前端開發 (/web-produce-frontend)

**已提供**：
- ✅ 完整色調系統 CSS 變數
- ✅ 組件樣式設計
- ✅ 佈局架構
- ✅ 響應式斷點

**需要實作**：
1. 將設計轉換為實際 HTML/CSS
2. 實作 Tab 切換 JavaScript
3. 實作更新按鈕功能
4. 資料綁定與顯示邏輯

### 給後端開發（Python/Shell Script）

**需要實作**：
1. `fetch-info-stream.py` - 爬蟲腳本
2. API endpoints (或 JSON 檔案生成)
3. 快取機制
4. 錯誤處理

---

**設計版本**: v2.0
**設計日期**: 2026-02-09
**設計師**: web-produce-designer
