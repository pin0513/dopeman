#!/usr/bin/env python3
"""
DopeMAN Python 環境檢查工具
檢查 Python 版本、套件依賴、確保打包不會有依賴問題
"""

import sys
import subprocess
from pathlib import Path

class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

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

def check_python_version():
    """檢查 Python 版本"""
    print_info("檢查 Python 版本...")

    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"

    print(f"   Python 版本: {version_str}")

    # 需要 Python 3.8+
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
        print_error(f"Python 版本過舊，需要 3.8+，當前: {version_str}")
        return False
    else:
        print_success(f"Python 版本符合要求 ({version_str} >= 3.8)")
        return True

def check_pip():
    """檢查 pip 是否安裝"""
    print_info("\n檢查 pip...")

    try:
        result = subprocess.run(['pip3', '--version'],
                              capture_output=True,
                              text=True,
                              check=True)
        print(f"   {result.stdout.strip()}")
        print_success("pip3 已安裝")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("pip3 未安裝")
        print_info("請執行: python3 -m ensurepip --upgrade")
        return False

def check_requirements():
    """檢查 requirements.txt 中的套件"""
    print_info("\n檢查套件依賴...")

    req_file = Path(__file__).parent / 'requirements.txt'

    if not req_file.exists():
        print_warning(f"requirements.txt 不存在: {req_file}")
        return True  # 如果沒有 requirements.txt，視為不需要額外套件

    print(f"   讀取: {req_file}")

    # 讀取 requirements.txt
    with open(req_file, 'r', encoding='utf-8') as f:
        requirements = []
        for line in f:
            line = line.strip()
            # 跳過註解和空行
            if line and not line.startswith('#'):
                # 提取套件名稱（忽略版本號）
                package = line.split('>=')[0].split('==')[0].split('<')[0].strip()
                requirements.append(package)

    if not requirements:
        print_success("沒有需要檢查的套件")
        return True

    print(f"   需要檢查 {len(requirements)} 個套件")

    missing = []
    installed = []

    for package in requirements:
        try:
            __import__(package)
            installed.append(package)
            print_success(f"{package} 已安裝")
        except ImportError:
            missing.append(package)
            print_error(f"{package} 未安裝")

    if missing:
        print(f"\n{Colors.YELLOW}缺少 {len(missing)} 個套件{Colors.NC}")
        print(f"\n{Colors.CYAN}安裝指令：{Colors.NC}")
        print(f"   pip3 install -r {req_file}")
        print(f"\n或個別安裝：")
        for package in missing:
            print(f"   pip3 install {package}")
        return False
    else:
        print_success(f"\n所有套件已安裝 ({len(installed)} 個)")
        return True

def install_requirements():
    """自動安裝缺失的套件"""
    req_file = Path(__file__).parent / 'requirements.txt'

    if not req_file.exists():
        print_warning("requirements.txt 不存在，跳過安裝")
        return True

    print_info(f"\n安裝套件依賴...")
    print(f"   執行: pip3 install -r {req_file}")

    try:
        result = subprocess.run(
            ['pip3', 'install', '-r', str(req_file)],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        print_success("套件安裝完成")
        return True
    except subprocess.CalledProcessError as e:
        print_error("套件安裝失敗")
        print(e.stderr)
        return False

def main():
    """主程式"""
    print_header("DopeMAN Python 環境檢查")

    # 檢查 Python 版本
    py_ok = check_python_version()

    # 檢查 pip
    pip_ok = check_pip()

    # 檢查套件
    req_ok = check_requirements()

    # 摘要
    print_header("檢查摘要")

    if py_ok and pip_ok and req_ok:
        print_success("✨ Python 環境完整！")
        return 0
    else:
        print_error("❌ Python 環境有問題")

        if not py_ok:
            print("   • Python 版本過舊")
        if not pip_ok:
            print("   • pip 未安裝")
        if not req_ok:
            print("   • 套件依賴缺失")

        # 詢問是否自動安裝
        if pip_ok and not req_ok:
            print(f"\n{Colors.YELLOW}是否自動安裝缺失的套件？{Colors.NC}")
            response = input("輸入 'y' 安裝，其他鍵跳過: ").strip().lower()

            if response == 'y':
                if install_requirements():
                    print_success("\n✨ 安裝完成！請重新執行檢查")
                    return 0

        return 1

if __name__ == '__main__':
    sys.exit(main())
