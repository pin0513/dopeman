#!/usr/bin/env python3
"""
DopeMAN API Server
提供 HTTP API 讓 Dashboard 可以觸發後端任務
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

class DopeMAN_API_Handler(SimpleHTTPRequestHandler):
    """處理 API 請求的 Handler"""

    def do_GET(self):
        """處理 GET 請求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # CORS headers
        self.send_cors_headers()

        if path == '/api/health-check':
            self.handle_health_check()
        elif path == '/api/status':
            self.handle_status()
        else:
            # 其他請求交給預設處理（靜態檔案）
            super().do_GET()

    def do_POST(self):
        """處理 POST 請求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # CORS headers
        self.send_cors_headers()

        if path == '/api/fix':
            self.handle_fix()
        elif path == '/api/reload':
            self.handle_reload()
        elif path == '/api/scan':
            self.handle_scan()
        elif path == '/api/update-data':
            self.handle_update_data()
        else:
            self.send_error(404, "API endpoint not found")

    def do_OPTIONS(self):
        """處理 OPTIONS 請求（CORS preflight）"""
        self.send_cors_headers()
        self.send_response(200)
        self.end_headers()

    def send_cors_headers(self):
        """發送 CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def send_json_response(self, data, status=200):
        """發送 JSON 回應"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def handle_health_check(self):
        """執行健康檢查"""
        try:
            # 執行 health-check.py
            result = subprocess.run(
                ['python3', 'health-check.py'],
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True,
                timeout=30
            )

            # 讀取報告
            report_file = Path.home() / '.claude' / 'memory' / 'dopeman' / 'health-check-report.json'
            if report_file.exists():
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
            else:
                report = {'error': 'Report file not found'}

            self.send_json_response({
                'success': result.returncode == 0,
                'report': report,
                'stdout': result.stdout,
                'stderr': result.stderr
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    def handle_fix(self):
        """執行自動修復"""
        try:
            # 執行 fix.py
            result = subprocess.run(
                ['python3', 'fix.py'],
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True,
                timeout=60
            )

            self.send_json_response({
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'message': '修復完成' if result.returncode == 0 else '修復失敗'
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    def handle_reload(self):
        """觸發重載提示"""
        try:
            # 執行 reload-skills.py
            result = subprocess.run(
                ['python3', 'reload-skills.py'],
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True,
                timeout=30
            )

            self.send_json_response({
                'success': True,
                'stdout': result.stdout,
                'message': 'Skills 環境健康，可以重載'
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    def handle_scan(self):
        """重新掃描資料"""
        try:
            # 執行 scan-real-data.py
            result = subprocess.run(
                ['python3', 'scan-real-data.py'],
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True,
                timeout=60
            )

            self.send_json_response({
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'message': '掃描完成' if result.returncode == 0 else '掃描失敗'
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    def handle_update_data(self):
        """更新個人資訊匯流資料"""
        try:
            # 執行 fetch-ptt-stocks-v2.py
            result = subprocess.run(
                ['python3', 'fetch-ptt-stocks-v2.py'],
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True,
                timeout=120
            )

            self.send_json_response({
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'message': '資料更新完成' if result.returncode == 0 else '資料更新失敗'
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    def handle_status(self):
        """獲取系統狀態"""
        try:
            home = Path.home()
            skills_dir = home / '.claude' / 'skills'

            # 統計 skills 數量
            skills_count = 0
            broken_count = 0

            if skills_dir.exists():
                for item in skills_dir.iterdir():
                    if item.is_symlink():
                        skills_count += 1
                        if not item.resolve().exists():
                            broken_count += 1

            self.send_json_response({
                'success': True,
                'status': {
                    'skills_count': skills_count,
                    'broken_count': broken_count,
                    'healthy': broken_count == 0,
                    'timestamp': datetime.now().isoformat()
                }
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, status=500)

def run_server(port=8891):
    """啟動伺服器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DopeMAN_API_Handler)

    print(f"🚀 DopeMAN API Server 已啟動")
    print(f"📍 位址: http://localhost:{port}")
    print(f"📡 API 端點:")
    print(f"   GET  /api/health-check  - 執行健康檢查")
    print(f"   POST /api/fix           - 執行自動修復")
    print(f"   POST /api/reload        - 觸發重載提示")
    print(f"   POST /api/scan          - 重新掃描資料")
    print(f"   POST /api/update-data   - 更新資訊匯流資料")
    print(f"   GET  /api/status        - 獲取系統狀態")
    print(f"\n按 Ctrl+C 停止伺服器\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n⏹️  伺服器已停止")
        httpd.shutdown()

if __name__ == '__main__':
    # 切換到 commands 目錄
    os.chdir(Path(__file__).parent)

    # 啟動伺服器
    run_server()
