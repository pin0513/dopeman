#!/usr/bin/env python3
"""
DopeMAN Reload Skills
提示並協助 Claude Code 重載技能組
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# 顏色輸出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def check_skills_health():
    """快速健康檢查"""
    print_header("🔍 快速健康檢查")

    home = Path.home()
    skills_dir = home / '.claude' / 'skills'

    if not skills_dir.exists():
        print_warning("全域 skills 目錄不存在")
        return False

    # 計算 skills 數量
    skills_count = 0
    broken_count = 0

    for item in skills_dir.iterdir():
        if item.is_symlink():
            skills_count += 1
            if not item.resolve().exists():
                broken_count += 1

    print_info(f"找到 {skills_count} 個 skills")

    if broken_count > 0:
        print_warning(f"發現 {broken_count} 個損壞的 symlinks")
        print(f"\n{Colors.YELLOW}建議先執行: /dopeman fix{Colors.END}\n")
        return False
    else:
        print_success("所有 symlinks 都正常")
        return True

def show_reload_instructions():
    """顯示重載指引"""
    print_header("🔄 Claude Code 重載 Skills 指引")

    print(f"{Colors.BOLD}方法 1：重啟 Claude Code（最可靠）{Colors.END}")
    print("   1. 儲存當前工作")
    print("   2. 完全關閉 Claude Code")
    print("   3. 重新開啟 Claude Code")
    print("   → Skills 會在啟動時自動載入\n")

    print(f"{Colors.BOLD}方法 2：重新開始對話（快速）{Colors.END}")
    print("   1. 在 Claude Code 中使用命令: /clear")
    print("   2. 或點擊「New Chat」開始新對話")
    print("   → 新對話會重新載入 skills\n")

    print(f"{Colors.BOLD}方法 3：驗證 Skills 已載入（檢查）{Colors.END}")
    print("   在 Claude Code 中執行任何 skill，例如:")
    print("   → /dopeman health-check")
    print("   → 如果可以執行，表示 skills 已正確載入\n")

def show_troubleshooting():
    """顯示疑難排解"""
    print_header("🔧 疑難排解")

    print(f"{Colors.BOLD}Q: Skills 重載後仍無法使用？{Colors.END}")
    print("A: 檢查以下項目:")
    print("   1. 執行 /dopeman health-check 確認沒有錯誤")
    print("   2. 確認 SKILL.md 格式正確（YAML frontmatter）")
    print("   3. 檢查檔案權限（chmod +x）")
    print("   4. 查看 Claude Code 的錯誤訊息\n")

    print(f"{Colors.BOLD}Q: 新增的 skill 看不到？{Colors.END}")
    print("A: 確認已建立 symlink:")
    print("   → /dopeman link")
    print("   → 然後重啟 Claude Code\n")

    print(f"{Colors.BOLD}Q: 修改 skill 內容後沒有更新？{Colors.END}")
    print("A: Skill 內容在對話開始時載入:")
    print("   → 使用 /clear 開始新對話")
    print("   → 或完全重啟 Claude Code\n")

def log_reload_event():
    """記錄重載事件"""
    home = Path.home()
    log_dir = home / '.claude' / 'memory' / 'dopeman'
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / 'reload-history.log'

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().isoformat()}] Skills reload triggered\n")

    print_info(f"已記錄到: {log_file}")

def main():
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          DopeMAN - Skills 重載助手                        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(Colors.END)

    # 1. 快速健康檢查
    health_ok = check_skills_health()

    if not health_ok:
        print(f"\n{Colors.RED}⚠️  發現問題，建議修復後再重載{Colors.END}\n")
        return 1

    # 2. 顯示重載指引
    show_reload_instructions()

    # 3. 顯示疑難排解
    show_troubleshooting()

    # 4. 記錄重載事件
    log_reload_event()

    # 5. 最終提示
    print_header("📝 總結")
    print_success("Skills 環境健康，可以安全重載")
    print(f"\n{Colors.BOLD}推薦步驟：{Colors.END}")
    print("   1. 在 Claude Code 中使用: /clear")
    print("   2. 測試任一 skill 確認已載入")
    print("   3. 如果還有問題，完全重啟 Claude Code\n")

    return 0

if __name__ == '__main__':
    sys.exit(main())
