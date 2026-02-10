#!/usr/bin/env python3
"""
DopeMAN - Official Skills/Teams Installer
安裝並管理官方 Skills 和 Teams
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# 顏色輸出
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def print_header(text):
    print(f"\n{Colors.CYAN}{'=' * 60}{Colors.NC}")
    print(f"{Colors.CYAN}{text:^60}{Colors.NC}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.NC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.NC}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.NC}")

def load_catalog():
    """載入官方目錄"""
    catalog_path = Path(__file__).parent / "official-catalog.json"

    if not catalog_path.exists():
        print_error(f"找不到官方目錄檔案: {catalog_path}")
        sys.exit(1)

    with open(catalog_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_installed(item):
    """檢查是否已安裝"""
    home = Path.home()

    if item['install_type'] == 'global_link':
        target = home / '.claude' / 'skills' / item['id']
    else:  # project
        target = home / 'AgentProjects' / item['id']

    return target.exists()

def get_repo_version(repo_path):
    """取得倉庫版本（最新 commit hash）"""
    try:
        result = subprocess.run(
            ['git', '-C', str(repo_path), 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return "unknown"

def display_catalog(catalog):
    """顯示官方目錄"""
    print_header("官方 Skills / Teams 目錄")

    for cat_id, category in catalog['categories'].items():
        print(f"\n{Colors.CYAN}📦 {category['name']}{Colors.NC}")
        print(f"   {category['description']}\n")

        for idx, item in enumerate(category['items'], 1):
            installed = check_installed(item)
            status = f"{Colors.GREEN}[已安裝]{Colors.NC}" if installed else f"{Colors.YELLOW}[未安裝]{Colors.NC}"

            print(f"   {idx}. {status} {item['name']}")
            print(f"      📝 {item['description']}")
            print(f"      🔗 {item['repo']}")
            print(f"      📂 類型: {item['type']} | 安裝方式: {item['install_type']}")

            if installed:
                home = Path.home()
                if item['install_type'] == 'global_link':
                    repo_path = home / '.claude' / 'skills' / item['id']
                else:
                    repo_path = home / 'AgentProjects' / item['id']

                version = get_repo_version(repo_path)
                print(f"      🏷️  版本: {version}")

            print()

def install_item(item):
    """安裝單個項目"""
    home = Path.home()

    # 決定安裝位置
    if item['install_type'] == 'global_link':
        target_dir = home / '.claude' / 'skills'
        target_path = target_dir / item['id']
    else:  # project
        target_dir = home / 'AgentProjects'
        target_path = target_dir / item['id']

    # 確保目標目錄存在
    target_dir.mkdir(parents=True, exist_ok=True)

    print_info(f"安裝 {item['name']} 到 {target_path}...")

    # 檢查是否已存在
    if target_path.exists():
        print_warning(f"目標已存在: {target_path}")
        response = input(f"   要覆蓋嗎？(y/N): ").strip().lower()
        if response != 'y':
            print_info("跳過安裝")
            return False

        # 備份現有版本
        backup_path = target_path.parent / f"{item['id']}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print_info(f"備份現有版本到: {backup_path}")
        subprocess.run(['mv', str(target_path), str(backup_path)], check=True)

    # 檢查是否有 subpath（Anthropic skills 的特殊處理）
    if 'subpath' in item:
        # 使用 sparse-checkout 只下載特定子目錄
        try:
            print_info(f"正在下載 {item['repo']} 的 {item['subpath']}...")

            # 初始化 git repo
            target_path.mkdir(parents=True, exist_ok=True)
            subprocess.run(['git', 'init'], cwd=target_path, check=True, capture_output=True)
            subprocess.run(['git', 'remote', 'add', 'origin', item['repo']], cwd=target_path, check=True, capture_output=True)

            # 啟用 sparse-checkout
            subprocess.run(['git', 'config', 'core.sparseCheckout', 'true'], cwd=target_path, check=True, capture_output=True)

            # 設定要下載的路徑
            sparse_checkout_file = target_path / '.git' / 'info' / 'sparse-checkout'
            sparse_checkout_file.parent.mkdir(parents=True, exist_ok=True)
            with open(sparse_checkout_file, 'w') as f:
                f.write(f"{item['subpath']}/*\n")

            # Pull 內容
            subprocess.run(['git', 'pull', 'origin', 'main'], cwd=target_path, check=True, capture_output=True)

            # 將子目錄內容移到根目錄
            subpath_dir = target_path / item['subpath']
            if subpath_dir.exists():
                for item_file in subpath_dir.iterdir():
                    item_file.rename(target_path / item_file.name)

                # 清理空目錄
                import shutil
                shutil.rmtree(target_path / item['subpath'].split('/')[0])

            print_success(f"下載完成")

        except subprocess.CalledProcessError as e:
            print_error(f"下載失敗: {e.stderr if e.stderr else str(e)}")
            return False
        except Exception as e:
            print_error(f"處理失敗: {e}")
            return False
    else:
        # 標準 clone（完整 repo）
        try:
            print_info(f"正在 clone {item['repo']}...")
            result = subprocess.run(
                ['git', 'clone', item['repo'], str(target_path)],
                capture_output=True,
                text=True,
                check=True
            )
            print_success(f"Clone 完成")
        except subprocess.CalledProcessError as e:
            print_error(f"Clone 失敗: {e.stderr}")
            return False

    # 如果是 global_link 類型，建立 commands 連結
    if item['install_type'] == 'global_link':
        commands_src = target_path / 'commands'
        if commands_src.exists():
            commands_target = home / '.claude' / 'commands' / item['id']
            commands_target.parent.mkdir(parents=True, exist_ok=True)

            if commands_target.exists():
                commands_target.unlink()

            print_info(f"建立 commands 連結: {commands_target}")
            commands_target.symlink_to(commands_src)

    # 更新 registry
    update_registry(item, str(target_path))

    print_success(f"✨ {item['name']} 安裝完成！")
    return True

def update_registry(item, install_path):
    """更新 skills registry"""
    registry_path = Path.home() / '.claude' / 'memory' / 'dopeman' / 'skills-registry.json'
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    # 讀取現有 registry
    if registry_path.exists():
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    else:
        registry = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "skills": []
        }

    # 檢查是否已存在
    existing = None
    for skill in registry['skills']:
        if skill['name'] == item['id']:
            existing = skill
            break

    # 更新或新增
    version = get_repo_version(install_path)

    skill_entry = {
        "name": item['id'],
        "display_name": item['name'],
        "path": install_path,
        "source": item['repo'],
        "version": version,
        "type": item['type'],
        "installed_at": datetime.now().isoformat(),
        "auto_update": item.get('auto_update', False),
        "has_update": False
    }

    if existing:
        registry['skills'][registry['skills'].index(existing)] = skill_entry
        print_info(f"Registry 已更新: {item['id']}")
    else:
        registry['skills'].append(skill_entry)
        print_info(f"Registry 已新增: {item['id']}")

    # 寫回 registry
    registry['last_updated'] = datetime.now().isoformat()
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def check_updates(catalog):
    """檢查官方 skills 更新"""
    print_header("檢查官方 Skills/Teams 更新")

    updates_available = []

    for cat_id, category in catalog['categories'].items():
        for item in category['items']:
            if not check_installed(item):
                continue

            home = Path.home()
            if item['install_type'] == 'global_link':
                repo_path = home / '.claude' / 'skills' / item['id']
            else:
                repo_path = home / 'AgentProjects' / item['id']

            print_info(f"檢查 {item['name']}...")

            # Fetch 最新
            try:
                subprocess.run(
                    ['git', '-C', str(repo_path), 'fetch', 'origin'],
                    capture_output=True,
                    check=True
                )

                # 比較版本
                result = subprocess.run(
                    ['git', '-C', str(repo_path), 'rev-list', '--count', 'HEAD..origin/main'],
                    capture_output=True,
                    text=True,
                    check=True
                )

                commits_behind = int(result.stdout.strip())

                if commits_behind > 0:
                    print_warning(f"   有 {commits_behind} 個新 commit 可更新")
                    updates_available.append((item, repo_path, commits_behind))
                else:
                    print_success(f"   已是最新版本")

            except Exception as e:
                print_error(f"   檢查失敗: {e}")

    if updates_available:
        print(f"\n{Colors.YELLOW}發現 {len(updates_available)} 個可更新項目{Colors.NC}\n")

        for idx, (item, repo_path, commits) in enumerate(updates_available, 1):
            print(f"{idx}. {item['name']} - {commits} 個新 commit")

        print(f"\n{Colors.CYAN}要更新這些項目嗎？{Colors.NC}")
        print("1) 全部更新")
        print("2) 選擇性更新")
        print("3) 略過")

        choice = input("\n請選擇 (1-3): ").strip()

        if choice == '1':
            for item, repo_path, _ in updates_available:
                update_item(item, repo_path)
        elif choice == '2':
            for item, repo_path, _ in updates_available:
                response = input(f"\n更新 {item['name']}? (y/N): ").strip().lower()
                if response == 'y':
                    update_item(item, repo_path)
    else:
        print_success("所有項目都已是最新版本！")

def update_item(item, repo_path):
    """更新單個項目"""
    print_info(f"更新 {item['name']}...")

    try:
        # Pull 最新
        subprocess.run(
            ['git', '-C', str(repo_path), 'pull', 'origin', 'main'],
            check=True
        )
        print_success(f"{item['name']} 更新完成")

        # 更新 registry
        update_registry(item, str(repo_path))

    except Exception as e:
        print_error(f"更新失敗: {e}")

def interactive_install(catalog):
    """互動式安裝介面"""
    print_header("安裝官方 Skills / Teams")

    # 收集所有項目
    all_items = []
    for cat_id, category in catalog['categories'].items():
        for item in category['items']:
            all_items.append((cat_id, category, item))

    # 顯示選項
    print(f"{Colors.CYAN}選擇安裝方式：{Colors.NC}\n")
    print("1) 依類別選擇")
    print("2) 全部安裝")
    print("3) 個別選擇")
    print("0) 取消")

    choice = input("\n請選擇 (0-3): ").strip()

    if choice == '0':
        print_info("取消安裝")
        return

    elif choice == '1':
        # 依類別選擇
        print(f"\n{Colors.CYAN}選擇要安裝的類別：{Colors.NC}\n")
        categories = list(catalog['categories'].items())

        for idx, (cat_id, category) in enumerate(categories, 1):
            installed_count = sum(1 for item in category['items'] if check_installed(item))
            total_count = len(category['items'])
            print(f"{idx}) {category['name']} ({installed_count}/{total_count} 已安裝)")
            print(f"   {category['description']}")

        print("0) 取消")

        cat_choice = input(f"\n請選擇類別 (0-{len(categories)}): ").strip()

        if cat_choice == '0':
            return

        try:
            cat_idx = int(cat_choice) - 1
            if 0 <= cat_idx < len(categories):
                cat_id, category = categories[cat_idx]

                print(f"\n{Colors.CYAN}安裝 {category['name']} 中的所有項目{Colors.NC}\n")
                for item in category['items']:
                    if not check_installed(item):
                        install_item(item)
                    else:
                        print_warning(f"{item['name']} 已安裝，跳過")
        except ValueError:
            print_error("無效的選擇")

    elif choice == '2':
        # 全部安裝
        print(f"\n{Colors.YELLOW}⚠️  要安裝所有官方 Skills/Teams 嗎？{Colors.NC}")
        confirm = input("這將下載約 ~500MB 的資料。確認嗎？ (yes/N): ").strip().lower()

        if confirm == 'yes':
            for cat_id, category, item in all_items:
                if not check_installed(item):
                    install_item(item)
                else:
                    print_warning(f"{item['name']} 已安裝，跳過")

    elif choice == '3':
        # 個別選擇
        print(f"\n{Colors.CYAN}選擇要安裝的項目（可多選，用空格分隔）：{Colors.NC}\n")

        for idx, (cat_id, category, item) in enumerate(all_items, 1):
            status = "[已安裝]" if check_installed(item) else ""
            print(f"{idx:2d}) {status:10s} {item['name']} - {item['description']}")

        selections = input(f"\n請輸入編號 (例如: 1 3 5): ").strip().split()

        for sel in selections:
            try:
                idx = int(sel) - 1
                if 0 <= idx < len(all_items):
                    cat_id, category, item = all_items[idx]
                    if not check_installed(item):
                        install_item(item)
                    else:
                        print_warning(f"{item['name']} 已安裝，跳過")
            except ValueError:
                print_error(f"無效的編號: {sel}")

def main():
    """主程式"""
    print_header("🎯 DopeMAN - 官方 Skills/Teams 管理器")

    # 載入目錄
    catalog = load_catalog()

    # 主選單
    while True:
        print(f"\n{Colors.CYAN}主選單：{Colors.NC}\n")
        print("1) 顯示官方目錄")
        print("2) 安裝 Skills/Teams")
        print("3) 檢查更新")
        print("4) 查看已安裝清單")
        print("0) 結束")

        choice = input("\n請選擇 (0-4): ").strip()

        if choice == '0':
            print_success("再見！")
            break

        elif choice == '1':
            display_catalog(catalog)

        elif choice == '2':
            interactive_install(catalog)

        elif choice == '3':
            check_updates(catalog)

        elif choice == '4':
            print_header("已安裝的官方 Skills/Teams")

            for cat_id, category in catalog['categories'].items():
                installed_items = [item for item in category['items'] if check_installed(item)]

                if installed_items:
                    print(f"\n{Colors.CYAN}📦 {category['name']}{Colors.NC}\n")

                    for item in installed_items:
                        home = Path.home()
                        if item['install_type'] == 'global_link':
                            repo_path = home / '.claude' / 'skills' / item['id']
                        else:
                            repo_path = home / 'AgentProjects' / item['id']

                        version = get_repo_version(repo_path)
                        print(f"   ✅ {item['name']}")
                        print(f"      📂 {repo_path}")
                        print(f"      🏷️  版本: {version}")
                        print()

        else:
            print_error("無效的選擇")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  已中斷{Colors.NC}")
        sys.exit(0)
    except Exception as e:
        print_error(f"錯誤: {e}")
        sys.exit(1)
