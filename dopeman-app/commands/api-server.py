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

        if path == '/api/fix':
            self.handle_fix()
        elif path == '/api/reload':
            self.handle_reload()
        elif path == '/api/scan':
            self.handle_scan()
        elif path == '/api/update-data':
            self.handle_update_data()
        elif path == '/api/install-official':
            self.handle_install_official()
        elif path == '/api/uninstall-official':
            self.handle_uninstall_official()
        elif path == '/api/update-official':
            self.handle_update_official()
        else:
            self.send_error(404, "API endpoint not found")

    def do_OPTIONS(self):
        """處理 OPTIONS 請求（CORS preflight）"""
        self.send_response(200)
        self.send_cors_headers()
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

    def handle_install_official(self):
        """安裝官方 Skill/Team - 方案 B：直接實作安裝邏輯"""
        try:
            # 讀取請求 body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            skill_id = data.get('id')
            skill_type = data.get('type')

            if not skill_id:
                self.send_json_response({
                    'success': False,
                    'error': 'Missing skill id'
                }, status=400)
                return

            # 載入 official-catalog.json
            catalog_path = Path(__file__).parent / 'official-catalog.json'
            with open(catalog_path, 'r', encoding='utf-8') as f:
                catalog = json.load(f)

            # 查找項目配置
            item_config = None
            for category_key, category in catalog['categories'].items():
                for item in category['items']:
                    if item['id'] == skill_id:
                        item_config = item
                        break
                if item_config:
                    break

            if not item_config:
                self.send_json_response({
                    'success': False,
                    'error': f'找不到 {skill_id} 的配置'
                }, status=404)
                return

            # 確定安裝路徑
            home = Path.home()
            if item_config['install_type'] == 'global_link':
                target_path = home / '.claude' / 'skills' / skill_id
            else:  # project
                target_path = home / 'AgentProjects' / skill_id

            # 檢查是否已存在
            if target_path.exists():
                self.send_json_response({
                    'success': False,
                    'error': f'{skill_id} 已存在於 {target_path}'
                }, status=409)
                return

            # 建立父目錄
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # 執行安裝
            repo_url = item_config['repo']
            subpath = item_config.get('subpath')

            install_log = []

            if subpath:
                # 使用 sparse-checkout（Anthropic skills）
                install_log.append(f"📦 使用 sparse-checkout 安裝 {skill_id}")
                install_log.append(f"📂 目標路徑: {target_path}")
                install_log.append(f"🔗 Repository: {repo_url}")
                install_log.append(f"📁 Subpath: {subpath}")

                # 初始化 git repo
                subprocess.run(['git', 'init'], cwd=target_path.parent, check=True, capture_output=True)
                subprocess.run(['git', 'init', str(target_path)], check=True, capture_output=True)

                # 設定 remote
                subprocess.run(
                    ['git', 'remote', 'add', 'origin', repo_url],
                    cwd=target_path,
                    check=True,
                    capture_output=True
                )

                # 啟用 sparse-checkout
                subprocess.run(
                    ['git', 'config', 'core.sparseCheckout', 'true'],
                    cwd=target_path,
                    check=True,
                    capture_output=True
                )

                # 寫入 sparse-checkout 配置
                sparse_checkout_file = target_path / '.git' / 'info' / 'sparse-checkout'
                sparse_checkout_file.parent.mkdir(parents=True, exist_ok=True)
                with open(sparse_checkout_file, 'w') as f:
                    f.write(f"{subpath}/*\n")

                # Pull 指定的 subpath
                result = subprocess.run(
                    ['git', 'pull', 'origin', 'main'],
                    cwd=target_path,
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if result.returncode != 0:
                    # 嘗試 master 分支
                    result = subprocess.run(
                        ['git', 'pull', 'origin', 'master'],
                        cwd=target_path,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )

                # 移動 subpath 內容到根目錄
                subpath_dir = target_path / subpath
                if subpath_dir.exists():
                    import shutil
                    for item in subpath_dir.iterdir():
                        shutil.move(str(item), str(target_path))

                    # 刪除空的 subpath 目錄結構
                    shutil.rmtree(target_path / subpath.split('/')[0])

                install_log.append("✅ Sparse-checkout 完成")

            else:
                # 一般 git clone
                install_log.append(f"📦 使用 git clone 安裝 {skill_id}")
                install_log.append(f"📂 目標路徑: {target_path}")
                install_log.append(f"🔗 Repository: {repo_url}")

                result = subprocess.run(
                    ['git', 'clone', repo_url, str(target_path)],
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if result.returncode != 0:
                    raise Exception(f"Git clone 失敗: {result.stderr}")

                install_log.append("✅ Git clone 完成")

            # 檢查安裝結果
            if item_config['type'] == 'skill':
                skill_md = target_path / 'SKILL.md'
                if not skill_md.exists():
                    raise Exception(f"安裝失敗：找不到 SKILL.md 於 {target_path}")
                install_log.append(f"✅ 驗證成功：SKILL.md 存在")
            else:  # team
                claude_md = target_path / 'CLAUDE.md'
                if not claude_md.exists():
                    raise Exception(f"安裝失敗：找不到 CLAUDE.md 於 {target_path}")
                install_log.append(f"✅ 驗證成功：CLAUDE.md 存在")

            self.send_json_response({
                'success': True,
                'message': f'✅ {skill_id} 安裝成功',
                'path': str(target_path),
                'log': '\n'.join(install_log)
            })

        except subprocess.TimeoutExpired:
            self.send_json_response({
                'success': False,
                'error': '安裝超時（120秒），可能網路較慢或 repository 太大'
            }, status=500)
        except Exception as e:
            # 如果失敗，清理已建立的目錄
            if 'target_path' in locals() and target_path.exists():
                import shutil
                shutil.rmtree(target_path, ignore_errors=True)

            self.send_json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    def handle_uninstall_official(self):
        """移除官方 Skill/Team"""
        try:
            # 讀取請求 body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            skill_id = data.get('id')
            skill_type = data.get('type')

            if not skill_id:
                self.send_json_response({
                    'success': False,
                    'error': 'Missing skill id'
                }, status=400)
                return

            # 判斷路徑
            home = Path.home()
            if skill_type == 'team':
                skill_path = home / 'AgentProjects' / skill_id
            else:
                skill_path = home / '.claude' / 'skills' / skill_id

            # 檢查是否存在
            if not skill_path.exists():
                self.send_json_response({
                    'success': False,
                    'error': f'{skill_id} 不存在於 {skill_path}'
                }, status=404)
                return

            # 備份到 .trash
            trash_dir = home / '.claude' / 'memory' / 'dopeman' / '.trash'
            trash_dir.mkdir(parents=True, exist_ok=True)

            import shutil
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = trash_dir / f"{skill_id}_{timestamp}"

            shutil.move(str(skill_path), str(backup_path))

            self.send_json_response({
                'success': True,
                'message': f'✅ {skill_id} 已移除',
                'backup': str(backup_path)
            })

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    def handle_update_official(self):
        """更新官方 Skill/Team"""
        try:
            # 讀取請求 body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            skill_id = data.get('id')

            if not skill_id:
                self.send_json_response({
                    'success': False,
                    'error': 'Missing skill id'
                }, status=400)
                return

            # 找到 skill 路徑
            home = Path.home()
            skill_path = home / '.claude' / 'skills' / skill_id

            if not skill_path.exists():
                skill_path = home / 'AgentProjects' / skill_id

            if not skill_path.exists():
                self.send_json_response({
                    'success': False,
                    'error': f'{skill_id} 不存在'
                }, status=404)
                return

            # 檢查是否為 git repo
            git_dir = skill_path / '.git'
            if not git_dir.exists():
                self.send_json_response({
                    'success': False,
                    'error': f'{skill_id} 不是 git repository，無法更新'
                }, status=400)
                return

            # 執行 git pull
            result = subprocess.run(
                ['git', 'pull'],
                cwd=skill_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            self.send_json_response({
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'message': f'✅ {skill_id} 更新成功' if result.returncode == 0 else f'❌ {skill_id} 更新失敗'
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
    print(f"   GET  /api/health-check       - 執行健康檢查")
    print(f"   GET  /api/status             - 獲取系統狀態")
    print(f"   POST /api/fix                - 執行自動修復")
    print(f"   POST /api/reload             - 觸發重載提示")
    print(f"   POST /api/scan               - 重新掃描資料")
    print(f"   POST /api/update-data        - 更新資訊匯流資料")
    print(f"   POST /api/install-official   - 安裝官方 Skill/Team")
    print(f"   POST /api/uninstall-official - 移除官方 Skill/Team")
    print(f"   POST /api/update-official    - 更新官方 Skill/Team")
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
