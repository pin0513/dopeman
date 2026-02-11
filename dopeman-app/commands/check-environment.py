#!/usr/bin/env python3
"""
DopeMAN 環境完整性檢查
檢查 .claude 環境是否完整，並自動修復問題
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

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

class EnvironmentChecker:
    def __init__(self):
        self.home = Path.home()
        self.claude_dir = self.home / '.claude'
        self.project_dir = Path(__file__).parent.parent.parent
        self.issues = []
        self.fixes = []

    def check_all(self):
        """執行所有檢查"""
        print_header("DopeMAN 環境檢查")

        self.check_claude_directory()
        self.check_skill_structure()
        self.check_commands()
        self.check_symlinks()
        self.check_data_files()
        self.check_python_environment()

        self.print_summary()

        if self.issues:
            print(f"\n{Colors.YELLOW}發現 {len(self.issues)} 個問題{Colors.NC}")
            return False
        else:
            print_success("環境檢查通過！")
            return True

    def check_claude_directory(self):
        """檢查 .claude 目錄結構"""
        print_info("檢查 .claude 目錄結構...")

        required_dirs = [
            self.claude_dir / 'skills',
            self.claude_dir / 'commands',
            self.claude_dir / 'memory' / 'dopeman'
        ]

        for dir_path in required_dirs:
            if not dir_path.exists():
                print_error(f"目錄不存在: {dir_path}")
                self.issues.append(f"Missing directory: {dir_path}")
                # 自動創建
                dir_path.mkdir(parents=True, exist_ok=True)
                self.fixes.append(f"Created directory: {dir_path}")
                print_success(f"已創建: {dir_path}")
            else:
                print_success(f"存在: {dir_path.relative_to(self.home)}")

    def check_skill_structure(self):
        """檢查 DopeMAN skill 結構"""
        print_info("\n檢查 DopeMAN Skill 結構...")

        global_skill_dir = self.claude_dir / 'skills' / 'dopeman'
        skill_md = global_skill_dir / 'SKILL.md'
        project_skill_md = self.project_dir / '.claude' / 'skills' / 'dopeman' / 'SKILL.md'

        # 檢查全域 skill 目錄
        if not global_skill_dir.exists():
            print_error(f"全域 skill 目錄不存在: {global_skill_dir}")
            self.issues.append("Global skill directory missing")
        else:
            print_success(f"全域 skill 目錄存在")

            # 檢查 SKILL.md
            if not skill_md.exists():
                print_error("SKILL.md 不存在")
                self.issues.append("SKILL.md missing")

                # 嘗試創建 symlink
                if project_skill_md.exists():
                    try:
                        # 創建相對 symlink
                        rel_path = os.path.relpath(project_skill_md, global_skill_dir)
                        os.symlink(rel_path, skill_md)
                        self.fixes.append(f"Created SKILL.md symlink")
                        print_success("已創建 SKILL.md symlink")
                    except Exception as e:
                        print_error(f"無法創建 symlink: {e}")
            else:
                print_success("SKILL.md 存在")

                # 檢查 YAML frontmatter
                try:
                    with open(skill_md, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if not content.startswith('---'):
                            print_warning("SKILL.md 缺少 YAML frontmatter")
                            self.issues.append("SKILL.md missing YAML frontmatter")
                        else:
                            print_success("SKILL.md 格式正確")
                except Exception as e:
                    print_error(f"無法讀取 SKILL.md: {e}")

    def check_commands(self):
        """檢查 commands 連結"""
        print_info("\n檢查 Commands...")

        commands_dir = self.claude_dir / 'commands'
        dopeman_command = commands_dir / 'dopeman.md'

        # 檢查是否有 dopeman command
        if not dopeman_command.exists():
            print_warning("dopeman command 不存在")
            # 這不是必需的，只是警告
        else:
            print_success("dopeman command 存在")

    def check_symlinks(self):
        """檢查並清理損壞的 symlinks"""
        print_info("\n檢查 Symlinks...")

        skills_dir = self.claude_dir / 'skills'
        broken_links = []

        if skills_dir.exists():
            for item in skills_dir.iterdir():
                if item.is_symlink():
                    target = item.resolve()
                    if not target.exists():
                        broken_links.append(item)
                        print_error(f"損壞的 symlink: {item.name} -> {target}")

        if broken_links:
            self.issues.append(f"Found {len(broken_links)} broken symlinks")
            print_warning(f"發現 {len(broken_links)} 個損壞的 symlinks")
        else:
            print_success("沒有損壞的 symlinks")

    def check_data_files(self):
        """檢查資料檔案"""
        print_info("\n檢查資料檔案...")

        data_file = self.project_dir / 'dopeman-app' / 'commands' / 'control-center-real-data.json'

        if not data_file.exists():
            print_warning(f"資料檔案不存在: {data_file.name}")
            print_info("需要執行一次 scan 來生成資料")
        else:
            print_success(f"資料檔案存在: {data_file.name}")

            # 檢查檔案是否過期（超過 24 小時）
            mtime = data_file.stat().st_mtime
            age_hours = (datetime.now().timestamp() - mtime) / 3600

            if age_hours > 24:
                print_warning(f"資料檔案已過期 ({age_hours:.1f} 小時)")
            else:
                print_success(f"資料檔案新鮮 ({age_hours:.1f} 小時)")

    def check_python_environment(self):
        """檢查 Python 環境"""
        print_info("\n檢查 Python 環境...")

        # 呼叫 check-python-env.py
        check_script = self.project_dir / 'dopeman-app' / 'commands' / 'check-python-env.py'

        if not check_script.exists():
            print_warning("check-python-env.py 不存在，跳過 Python 環境檢查")
            return

        try:
            import subprocess
            result = subprocess.run(
                ['python3', str(check_script)],
                capture_output=True,
                text=True,
                cwd=check_script.parent
            )

            # 顯示輸出（簡化版）
            if result.returncode == 0:
                print_success("Python 環境完整")
            else:
                print_warning("Python 環境有問題（詳細資訊請執行 python3 check-python-env.py）")
                self.issues.append("Python dependencies missing")

        except Exception as e:
            print_warning(f"無法執行 Python 環境檢查: {e}")

    def print_summary(self):
        """打印摘要"""
        print_header("檢查摘要")

        if not self.issues:
            print_success("所有檢查通過！")
        else:
            print_error(f"發現 {len(self.issues)} 個問題：")
            for issue in self.issues:
                print(f"  • {issue}")

        if self.fixes:
            print(f"\n{Colors.GREEN}已自動修復 {len(self.fixes)} 個問題：{Colors.NC}")
            for fix in self.fixes:
                print(f"  • {fix}")

def main():
    checker = EnvironmentChecker()
    success = checker.check_all()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
