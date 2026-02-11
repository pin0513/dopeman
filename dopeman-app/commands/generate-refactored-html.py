#!/usr/bin/env python3
"""
生成重構後的 Dashboard HTML
將原始 HTML 拆分為：HTML + 外部 CSS + 外部 JS
"""

import re
from pathlib import Path

# 檔案路徑
ORIGINAL_HTML = Path(__file__).parent / 'control-center-real.html'
OUTPUT_HTML = Path(__file__).parent / 'control-center-v2.html'
OUTPUT_CSS = Path(__file__).parent / 'css' / 'dashboard-legacy.css'
OUTPUT_JS = Path(__file__).parent / 'js' / 'dashboard-legacy.js'

def main():
    print("🔄 開始生成重構後的 HTML...")

    # 讀取原始檔案
    with open(ORIGINAL_HTML, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取 CSS（<style> 標籤內的內容）
    css_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    css_content = css_match.group(1).strip() if css_match else ''

    # 提取 JavaScript（<script> 標籤內的內容）
    js_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
    js_content = js_match.group(1).strip() if js_match else ''

    # 提取 HTML Body
    body_match = re.search(r'<body>(.*?)</body>', content, re.DOTALL)
    body_content = body_match.group(1).strip() if body_match else ''

    # 儲存 CSS
    OUTPUT_CSS.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSS, 'w', encoding='utf-8') as f:
        f.write(f"""/**
 * DopeMAN Dashboard - Legacy Styles
 * 從原始 control-center-real.html 提取的樣式
 * ⚠️ 待逐步遷移到模組化組件樣式
 */

{css_content}
""")
    print(f"✅ CSS 已儲存: {OUTPUT_CSS}")

    # 儲存 JavaScript
    OUTPUT_JS.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JS, 'w', encoding='utf-8') as f:
        f.write(f"""/**
 * DopeMAN Dashboard - Legacy JavaScript
 * 從原始 control-center-real.html 提取的程式碼
 * ⚠️ 待逐步遷移到模組化架構
 */

{js_content}
""")
    print(f"✅ JavaScript 已儲存: {OUTPUT_JS}")

    # 生成新的 HTML
    new_html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DopeMAN - Skills Control Center (v2 Refactored)</title>

    <!-- ✅ 重構後的模組化 CSS -->
    <link rel="stylesheet" href="css/dashboard-variables.css">
    <link rel="stylesheet" href="css/dashboard-layout.css">

    <!-- ⏳ 原始樣式（逐步遷移中） -->
    <link rel="stylesheet" href="css/dashboard-legacy.css">
</head>
<body>
{body_content}

<!-- ✅ 重構後的模組化 JavaScript -->
<script src="js/dashboard-config.js"></script>
<script src="js/dashboard-state.js"></script>
<script src="js/dashboard-api.js"></script>

<!-- ⏳ 原始程式碼（逐步遷移中） -->
<script src="js/dashboard-legacy.js"></script>

<script>
    /**
     * 應用程式初始化
     * 整合新舊系統
     */
    console.log('✅ DopeMAN Dashboard v2 (Refactored) loaded');
    console.log('📦 Modules:', {{
        Config: typeof DashboardConfig !== 'undefined',
        State: typeof DashboardState !== 'undefined',
        API: typeof DashboardAPI !== 'undefined'
    }});
</script>
</body>
</html>
"""

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f"✅ HTML 已儲存: {OUTPUT_HTML}")
    print("\n" + "=" * 60)
    print("🎉 重構完成！")
    print("=" * 60)
    print(f"\n📊 檔案大小統計:")
    print(f"   原始 HTML: {ORIGINAL_HTML.stat().st_size:,} bytes")
    print(f"   新版 HTML: {OUTPUT_HTML.stat().st_size:,} bytes")
    print(f"   CSS 檔案:  {OUTPUT_CSS.stat().st_size:,} bytes")
    print(f"   JS 檔案:   {OUTPUT_JS.stat().st_size:,} bytes")
    print(f"\n💡 使用方式:")
    print(f"   開啟瀏覽器: open {OUTPUT_HTML.name}")

if __name__ == '__main__':
    main()
