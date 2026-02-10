#!/usr/bin/env python3
"""
Control Center HTTP Server
提供 Dashboard 頁面與重新掃描 API
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

PORT = 8891
COMMANDS_DIR = Path(__file__).parent

class ControlCenterHandler(SimpleHTTPRequestHandler):
    """自訂 HTTP Handler 處理重新掃描請求"""

    def do_GET(self):
        """處理 GET 請求"""
        parsed_path = urlparse(self.path)

        # 移除查詢參數，只保留路徑
        clean_path = parsed_path.path

        # 處理根路徑，自動導向 control-center-real.html
        if clean_path == '/' or clean_path == '':
            clean_path = '/control-center-real.html'
            self.path = clean_path

        # 設定正確的工作目錄
        os.chdir(COMMANDS_DIR)

        # 使用父類的方法處理靜態檔案
        return super().do_GET()

    def do_POST(self):
        """處理 POST 請求 - 重新掃描"""
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/api/rescan':
            # 執行重新掃描
            try:
                print("🔄 開始重新掃描...")

                # 執行 scan-real-data.py
                scan_script = COMMANDS_DIR / "scan-real-data.py"
                result = subprocess.run(
                    [sys.executable, str(scan_script)],
                    cwd=str(COMMANDS_DIR),
                    capture_output=True,
                    text=True,
                    timeout=60  # 60秒超時
                )

                if result.returncode == 0:
                    print("✅ 掃描完成！")

                    # 回傳成功回應
                    response = {
                        "success": True,
                        "message": "掃描完成",
                        "output": result.stdout
                    }

                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                else:
                    print(f"❌ 掃描失敗: {result.stderr}")

                    response = {
                        "success": False,
                        "message": "掃描失敗",
                        "error": result.stderr
                    }

                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

            except subprocess.TimeoutExpired:
                print("❌ 掃描超時")
                response = {
                    "success": False,
                    "message": "掃描超時（超過60秒）"
                }
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

            except Exception as e:
                print(f"❌ 發生錯誤: {e}")
                response = {
                    "success": False,
                    "message": f"發生錯誤: {str(e)}"
                }
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_error(404, "API endpoint not found")

    def do_OPTIONS(self):
        """處理 OPTIONS 請求 (CORS preflight)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        """自訂日誌格式"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server():
    """啟動 HTTP 伺服器"""
    os.chdir(COMMANDS_DIR)

    server = HTTPServer(('localhost', PORT), ControlCenterHandler)

    print("=" * 60)
    print("🎛️  DopeMAN Control Center Server")
    print("=" * 60)
    print(f"📍 Server running at: http://localhost:{PORT}")
    print(f"📂 Serving from: {COMMANDS_DIR}")
    print(f"🌐 Dashboard: http://localhost:{PORT}/control-center-real.html")
    print(f"🔄 API Endpoint: http://localhost:{PORT}/api/rescan")
    print("=" * 60)
    print("按 Ctrl+C 停止伺服器")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 伺服器已停止")
        server.shutdown()


if __name__ == "__main__":
    run_server()
