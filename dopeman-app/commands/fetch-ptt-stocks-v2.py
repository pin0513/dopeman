#!/usr/bin/env python3
"""
DopeMAN Info Stream - PTT + 台股爬蟲 v2
使用 yfinance 取得真實台股資料
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import yfinance as yf
import pandas as pd

# PTT 基本設定
PTT_BASE_URL = "https://www.ptt.cc"
PTT_OVER18_COOKIE = {"over18": "1"}

# 台股熱門股票代碼（用於取得漲跌榜）
TW_POPULAR_STOCKS = [
    '2330', '2317', '2454', '2412', '2882', '2881', '2891', '2303',
    '2308', '2886', '3008', '2002', '1301', '1303', '2357', '2327',
    '2382', '2395', '2408', '6505', '2801', '2884', '2892', '2887',
    '2323', '3711', '2324', '2603', '5880', '4904', '2379', '2356',
    '2609', '2615', '3034', '2376', '2409', '3045', '2912', '2347',
    '2354', '3231', '2207', '2301', '1216', '1326', '2353', '2344',
    '2360', '2890'  # 前50大熱門股票
]


def fetch_ptt_hot_articles(board="Gossiping", limit=10):
    """
    爬取 PTT 看板熱門文章

    Args:
        board: 看板名稱（預設：Gossiping 八卦板）
        limit: 取前幾筆（預設：10）

    Returns:
        list: 熱門文章列表
    """
    print(f"🔍 爬取 PTT {board} 板熱門文章...")

    try:
        url = f"{PTT_BASE_URL}/bbs/{board}/index.html"

        # 加入更完整的 headers 避免被擋
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        response = requests.get(
            url,
            cookies=PTT_OVER18_COOKIE,
            headers=headers,
            timeout=15,
            allow_redirects=True
        )
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'html.parser')

        articles = []
        for article_div in soup.find_all('div', class_='r-ent'):
            # 標題
            title_tag = article_div.find('div', class_='title')
            if not title_tag or not title_tag.find('a'):
                continue

            title = title_tag.find('a').text.strip()
            link = PTT_BASE_URL + title_tag.find('a')['href']

            # 推文數
            push_tag = article_div.find('div', class_='nrec')
            push_count = 0
            if push_tag:
                push_text = push_tag.text.strip()
                if push_text == '爆':
                    push_count = 100  # 爆文
                elif push_text.startswith('X'):
                    push_count = -100  # XX
                elif push_text:
                    try:
                        push_count = int(push_text)
                    except:
                        push_count = 0

            # 作者
            author_tag = article_div.find('div', class_='author')
            author = author_tag.text.strip() if author_tag else 'Unknown'

            # 日期
            date_tag = article_div.find('div', class_='date')
            date = date_tag.text.strip() if date_tag else ''

            # 只取有推文的文章（表示有熱度）
            if push_count > 0 or '爆' in str(push_tag):
                articles.append({
                    'title': title,
                    'board': board,
                    'push_count': push_count,
                    'author': author,
                    'date': date,
                    'url': link
                })

            if len(articles) >= limit:
                break

        # 依推文數排序
        articles.sort(key=lambda x: x['push_count'], reverse=True)

        print(f"✅ 成功爬取 {len(articles)} 篇熱門文章")
        return articles[:limit]

    except Exception as e:
        print(f"❌ 爬取 PTT 失敗: {e}")
        print("⚠️  使用 Mock 資料")

        # 返回 Mock 資料供測試
        return [
            {
                'title': '[爆卦] 台積電宣布重大突破',
                'board': board,
                'push_count': 1200,
                'author': 'mock_user1',
                'date': '2/10',
                'url': 'https://www.ptt.cc/bbs/Gossiping/M.xxx.A.html'
            },
            {
                'title': '[問卦] 為什麼程式設計師都喜歡深色主題？',
                'board': board,
                'push_count': 850,
                'author': 'mock_user2',
                'date': '2/10',
                'url': 'https://www.ptt.cc/bbs/Gossiping/M.xxx.B.html'
            },
        ]


def fetch_tw_stock_data_yfinance(symbols, limit=30):
    """
    使用 yfinance 批次取得台股資料

    Args:
        symbols: 股票代碼列表
        limit: 回傳前幾筆

    Returns:
        list: 股票資料列表
    """
    print(f"🔍 使用 yfinance 取得台股資料...")

    stocks_data = []

    # 批次取得資料（加上 .TW 後綴）
    tw_symbols = [f"{symbol}.TW" for symbol in symbols]

    try:
        # 使用 yfinance 批次下載
        tickers = yf.Tickers(' '.join(tw_symbols))

        for symbol in symbols:
            try:
                ticker_symbol = f"{symbol}.TW"
                ticker = yf.Ticker(ticker_symbol)

                # 取得基本資訊
                info = ticker.info

                # 取得歷史資料（最近2天，用於計算漲跌）
                hist = ticker.history(period='2d')

                if hist.empty or len(hist) < 1:
                    continue

                # 最新價格
                latest_price = hist['Close'].iloc[-1]

                # 計算漲跌
                if len(hist) >= 2:
                    prev_price = hist['Close'].iloc[-2]
                    change = latest_price - prev_price
                    change_percent = (change / prev_price) * 100
                else:
                    change = 0
                    change_percent = 0

                # 成交量
                volume = hist['Volume'].iloc[-1]
                volume_str = f"{int(volume / 1000):,}張" if volume > 0 else "N/A"

                # 股票名稱（從 info 取得）
                name = info.get('longName', info.get('shortName', symbol))
                if not name or name == symbol:
                    # 如果取不到名稱，使用預設對照表
                    name_map = {
                        '2330': '台積電', '2317': '鴻海', '2454': '聯發科',
                        '2412': '中華電', '2882': '國泰金', '2881': '富邦金',
                        '2891': '中信金', '2303': '聯電', '2308': '台達電',
                        '2886': '兆豐金'
                    }
                    name = name_map.get(symbol, symbol)

                stocks_data.append({
                    'symbol': symbol,
                    'name': name,
                    'price': round(latest_price, 2),
                    'change': round(change, 2),
                    'change_percent': round(change_percent, 2),
                    'volume': volume_str,
                    'type': 'stock'
                })

            except Exception as e:
                # 個別股票失敗不影響整體
                continue

        print(f"✅ 成功取得 {len(stocks_data)} 檔股票資料")
        return stocks_data

    except Exception as e:
        print(f"❌ yfinance 取得資料失敗: {e}")
        return []


def fetch_tw_stock_top_gainers(limit=30):
    """
    取得台股漲幅排行榜（前30名）
    使用 yfinance
    """
    print(f"📈 取得台股漲幅排行榜...")

    # 取得所有熱門股票資料
    all_stocks = fetch_tw_stock_data_yfinance(TW_POPULAR_STOCKS, limit=50)

    if not all_stocks:
        print("⚠️  yfinance 失敗，使用 Mock 資料")
        return [
            {
                'symbol': '2330',
                'name': '台積電',
                'price': 580.0,
                'change': 18.0,
                'change_percent': 3.2,
                'volume': '45,234張',
                'type': 'stock'
            },
            {
                'symbol': '2454',
                'name': '聯發科',
                'price': 920.0,
                'change': 25.0,
                'change_percent': 2.8,
                'volume': '12,456張',
                'type': 'stock'
            },
        ]

    # 依漲幅排序
    gainers = sorted(
        [s for s in all_stocks if s['change_percent'] > 0],
        key=lambda x: x['change_percent'],
        reverse=True
    )

    return gainers[:limit]


def fetch_tw_stock_top_losers(limit=30):
    """
    取得台股跌幅排行榜（前30名）
    使用 yfinance
    """
    print(f"📉 取得台股跌幅排行榜...")

    # 取得所有熱門股票資料（重用已取得的資料）
    all_stocks = fetch_tw_stock_data_yfinance(TW_POPULAR_STOCKS, limit=50)

    if not all_stocks:
        print("⚠️  yfinance 失敗，使用 Mock 資料")
        return [
            {
                'symbol': '2412',
                'name': '中華電',
                'price': 115.0,
                'change': -2.5,
                'change_percent': -2.1,
                'volume': '23,456張',
                'type': 'stock'
            },
        ]

    # 依跌幅排序
    losers = sorted(
        [s for s in all_stocks if s['change_percent'] < 0],
        key=lambda x: x['change_percent']
    )

    return losers[:limit]


def fetch_tw_stock_indices():
    """
    取得台股重要指數（加權指數）
    使用 yfinance
    """
    print(f"📊 取得台股重要指數...")

    try:
        # 台灣加權指數代碼
        taiex = yf.Ticker("^TWII")

        # 取得最近資料
        hist = taiex.history(period='2d')

        if hist.empty or len(hist) < 1:
            raise Exception("無法取得指數資料")

        latest_price = hist['Close'].iloc[-1]

        # 計算漲跌
        if len(hist) >= 2:
            prev_price = hist['Close'].iloc[-2]
            change = latest_price - prev_price
            change_percent = (change / prev_price) * 100
        else:
            change = 0
            change_percent = 0

        indices = {
            'taiex': {
                'name': '加權指數',
                'value': round(latest_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2)
            }
        }

        print(f"✅ 成功取得指數資料")
        return indices

    except Exception as e:
        print(f"❌ 取得指數失敗: {e}")
        return {
            'taiex': {
                'name': '加權指數',
                'value': 0,
                'change': 0,
                'change_percent': 0
            }
        }


def save_to_json(data, filename='info-stream-data.json'):
    """儲存資料到 JSON 檔案"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 資料已儲存到 {filename}")
    except Exception as e:
        print(f"❌ 儲存失敗: {e}")


def main():
    """主程式"""
    print("=" * 60)
    print("🚀 DopeMAN Info Stream - PTT + 台股爬蟲 v2 (yfinance)")
    print("=" * 60)
    print()

    # 1. 爬取 PTT
    ptt_gossiping = fetch_ptt_hot_articles(board="Gossiping", limit=10)
    time.sleep(2)  # 避免太頻繁請求

    # 2. 取得台股資料（使用 yfinance）
    tw_gainers = fetch_tw_stock_top_gainers(limit=30)
    time.sleep(1)

    tw_losers = fetch_tw_stock_top_losers(limit=30)
    time.sleep(1)

    tw_indices = fetch_tw_stock_indices()

    # 3. 組裝資料
    data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'version': '2.0.0',
            'source': 'yfinance'
        },
        'social': {
            'ptt': {
                'gossiping': {
                    'trending': ptt_gossiping,
                    'count': len(ptt_gossiping)
                }
            }
        },
        'stocks': {
            'tw': {
                'top_gainers': tw_gainers,
                'top_losers': tw_losers,
                'indices': tw_indices
            }
        }
    }

    # 4. 儲存到 JSON
    save_to_json(data)

    print()
    print("=" * 60)
    print("✅ 爬蟲執行完成！")
    print("=" * 60)
    print(f"📊 統計：")
    print(f"   PTT 八卦板熱門: {len(ptt_gossiping)} 篇")
    print(f"   台股漲幅榜: {len(tw_gainers)} 檔")
    print(f"   台股跌幅榜: {len(tw_losers)} 檔")
    print(f"   指數: 加權指數 {tw_indices['taiex']['value']}")
    print()


if __name__ == '__main__':
    main()
