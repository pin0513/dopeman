#!/usr/bin/env python3
"""
DopeMAN Health Check
檢查技能組載入狀態與全域連結健康度
"""

import os
import sys
import json
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

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

class HealthChecker:
    def __init__(self):
        self.home = Path.home()
        self.global_skills_dir = self.home / '.claude' / 'skills'
        self.issues = {
            'critical': [],
            'warning': [],
            'info': []
        }
        self.stats = {
            'total_skills': 0,
            'healthy_skills': 0,
            'broken_symlinks': 0,
            'missing_frontmatter': 0,
            'duplicate_names': 0
        }

    def check_skills_directory(self):
        """檢查全域 skills 目錄"""
        print_header("📂 檢查全域 Skills 目錄")

        if not self.global_skills_dir.exists():
            self.issues['critical'].append("全域 skills 目錄不存在")
            print_error(f"目錄不存在: {self.global_skills_dir}")
            return False

        print_success(f"目錄存在: {self.global_skills_dir}")
        return True

    def check_symlinks(self):
        """檢查 symlinks 健康度"""
        print_header("🔗 檢查 Symlinks 健康度")

        broken_links = []
        valid_links = []

        for item in self.global_skills_dir.iterdir():
            if item.is_symlink():
                self.stats['total_skills'] += 1
                target = item.resolve()

                # 檢查 symlink 是否有效
                if not target.exists():
                    broken_links.append({
                        'name': item.name,
                        'link': str(item),
                        'target': str(target)
                    })
                    self.stats['broken_symlinks'] += 1
                    self.issues['critical'].append(f"損壞的 symlink: {item.name} -> {target}")
                else:
                    valid_links.append(item.name)
                    self.stats['healthy_skills'] += 1

        # 輸出結果
        if broken_links:
            print_error(f"發現 {len(broken_links)} 個損壞的 symlinks:")
            for link in broken_links:
                print(f"   {Colors.RED}• {link['name']}{Colors.END}")
                print(f"     連結: {link['link']}")
                print(f"     目標: {link['target']} (不存在)")
        else:
            print_success("所有 symlinks 都正常")

        if valid_links:
            print_info(f"正常的 symlinks: {len(valid_links)} 個")

        return len(broken_links) == 0

    def check_skill_structure(self):
        """檢查 skill 結構完整性"""
        print_header("📋 檢查 Skill 結構完整性")

        issues = []

        for skill_dir in self.global_skills_dir.iterdir():
            if not skill_dir.is_symlink():
                continue

            # 解析 symlink 目標
            try:
                target = skill_dir.resolve()
                if not target.exists():
                    continue  # 已在 check_symlinks 中處理

                # 檢查 SKILL.md 是否存在
                skill_md = target / 'SKILL.md'
                if not skill_md.exists():
                    issues.append({
                        'skill': skill_dir.name,
                        'issue': 'SKILL.md 不存在',
                        'severity': 'critical'
                    })
                    self.issues['critical'].append(f"{skill_dir.name}: SKILL.md 不存在")
                    continue

                # 檢查 YAML frontmatter
                with open(skill_md, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.startswith('---'):
                        issues.append({
                            'skill': skill_dir.name,
                            'issue': '缺少 YAML frontmatter',
                            'severity': 'warning'
                        })
                        self.stats['missing_frontmatter'] += 1
                        self.issues['warning'].append(f"{skill_dir.name}: 缺少 YAML frontmatter")
                    else:
                        # 檢查必要欄位
                        if 'name:' not in content.split('---')[1]:
                            issues.append({
                                'skill': skill_dir.name,
                                'issue': 'YAML 缺少 name 欄位',
                                'severity': 'warning'
                            })
                            self.issues['warning'].append(f"{skill_dir.name}: YAML 缺少 name 欄位")

                        if 'description:' not in content.split('---')[1]:
                            issues.append({
                                'skill': skill_dir.name,
                                'issue': 'YAML 缺少 description 欄位',
                                'severity': 'warning'
                            })
                            self.issues['warning'].append(f"{skill_dir.name}: YAML 缺少 description 欄位")

            except Exception as e:
                issues.append({
                    'skill': skill_dir.name,
                    'issue': f'讀取失敗: {str(e)}',
                    'severity': 'critical'
                })
                self.issues['critical'].append(f"{skill_dir.name}: 讀取失敗 - {str(e)}")

        # 輸出結果
        if issues:
            critical_issues = [i for i in issues if i['severity'] == 'critical']
            warning_issues = [i for i in issues if i['severity'] == 'warning']

            if critical_issues:
                print_error(f"發現 {len(critical_issues)} 個嚴重問題:")
                for issue in critical_issues:
                    print(f"   {Colors.RED}• {issue['skill']}: {issue['issue']}{Colors.END}")

            if warning_issues:
                print_warning(f"發現 {len(warning_issues)} 個警告:")
                for issue in warning_issues:
                    print(f"   {Colors.YELLOW}• {issue['skill']}: {issue['issue']}{Colors.END}")
        else:
            print_success("所有 skill 結構都正常")

        return len([i for i in issues if i['severity'] == 'critical']) == 0

    def check_duplicate_names(self):
        """檢查重複的 skill 名稱"""
        print_header("🔍 檢查重複的 Skill 名稱")

        skill_names = {}
        duplicates = []

        for skill_dir in self.global_skills_dir.iterdir():
            if not skill_dir.is_symlink():
                continue

            name = skill_dir.name
            if name in skill_names:
                skill_names[name].append(str(skill_dir))
                if name not in duplicates:
                    duplicates.append(name)
            else:
                skill_names[name] = [str(skill_dir)]

        if duplicates:
            print_warning(f"發現 {len(duplicates)} 個重複的名稱:")
            for dup in duplicates:
                print(f"   {Colors.YELLOW}• {dup}:{Colors.END}")
                for path in skill_names[dup]:
                    print(f"     - {path}")
                self.stats['duplicate_names'] += 1
                self.issues['warning'].append(f"重複的 skill 名稱: {dup}")
        else:
            print_success("沒有重複的 skill 名稱")

        return len(duplicates) == 0

    def check_claude_code_load(self):
        """檢查 Claude Code 是否能載入 skills（模擬）"""
        print_header("🤖 模擬 Claude Code 載入檢查")

        # 這裡模擬檢查，實際上 Claude Code 會在啟動時載入
        # 我們檢查常見的載入失敗原因

        load_issues = []

        for skill_dir in self.global_skills_dir.iterdir():
            if not skill_dir.is_symlink():
                continue

            try:
                target = skill_dir.resolve()
                if not target.exists():
                    load_issues.append(f"{skill_dir.name}: 目標不存在")
                    continue

                skill_md = target / 'SKILL.md'
                if not skill_md.exists():
                    load_issues.append(f"{skill_dir.name}: SKILL.md 不存在")
                    continue

                # 嘗試讀取檔案（檢查權限）
                with open(skill_md, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) == 0:
                        load_issues.append(f"{skill_dir.name}: SKILL.md 是空檔案")

            except PermissionError:
                load_issues.append(f"{skill_dir.name}: 權限不足")
            except UnicodeDecodeError:
                load_issues.append(f"{skill_dir.name}: 編碼錯誤")
            except Exception as e:
                load_issues.append(f"{skill_dir.name}: {str(e)}")

        if load_issues:
            print_error(f"發現 {len(load_issues)} 個可能的載入問題:")
            for issue in load_issues:
                print(f"   {Colors.RED}• {issue}{Colors.END}")
                self.issues['critical'].append(f"載入問題: {issue}")
        else:
            print_success("所有 skills 應該可以正常載入")

        return len(load_issues) == 0

    def generate_report(self):
        """生成健康報告"""
        print_header("📊 健康檢查報告")

        print(f"{Colors.BOLD}統計資訊:{Colors.END}")
        print(f"  總 Skills 數: {self.stats['total_skills']}")
        print(f"  健康的 Skills: {self.stats['healthy_skills']}")
        print(f"  損壞的 Symlinks: {self.stats['broken_symlinks']}")
        print(f"  缺少 Frontmatter: {self.stats['missing_frontmatter']}")
        print(f"  重複的名稱: {self.stats['duplicate_names']}")

        print(f"\n{Colors.BOLD}問題摘要:{Colors.END}")
        print(f"  🔴 嚴重問題: {len(self.issues['critical'])}")
        print(f"  🟡 警告: {len(self.issues['warning'])}")
        print(f"  🔵 資訊: {len(self.issues['info'])}")

        # 健康分數
        total_checks = self.stats['total_skills']
        if total_checks > 0:
            health_score = (self.stats['healthy_skills'] / total_checks) * 100

            if health_score >= 90:
                color = Colors.GREEN
                status = "優秀"
            elif health_score >= 70:
                color = Colors.YELLOW
                status = "良好"
            else:
                color = Colors.RED
                status = "需要改善"

            print(f"\n{Colors.BOLD}健康分數: {color}{health_score:.1f}%{Colors.END} ({status})")

        # 建議動作
        if self.issues['critical']:
            print(f"\n{Colors.BOLD}{Colors.RED}建議動作:{Colors.END}")
            print_error("執行 /dopeman fix 來自動修復問題")
        elif self.issues['warning']:
            print(f"\n{Colors.BOLD}{Colors.YELLOW}建議動作:{Colors.END}")
            print_warning("檢查警告項目，確認是否需要手動處理")
        else:
            print(f"\n{Colors.BOLD}{Colors.GREEN}狀態:{Colors.END}")
            print_success("環境健康，無需修復")

        # 儲存報告
        self.save_report()

    def save_report(self):
        """儲存報告到檔案"""
        report_dir = self.home / '.claude' / 'memory' / 'dopeman'
        report_dir.mkdir(parents=True, exist_ok=True)

        report_file = report_dir / 'health-check-report.json'

        report = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'issues': self.issues,
            'health_score': (self.stats['healthy_skills'] / max(self.stats['total_skills'], 1)) * 100
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n💾 報告已儲存: {report_file}")

    def run(self):
        """執行完整健康檢查"""
        print(f"{Colors.BOLD}{Colors.BLUE}")
        print("╔════════════════════════════════════════════════════════════╗")
        print("║          DopeMAN - Skills 健康檢查系統                    ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print(Colors.END)

        all_passed = True

        # 1. 檢查目錄
        if not self.check_skills_directory():
            return False

        # 2. 檢查 symlinks
        if not self.check_symlinks():
            all_passed = False

        # 3. 檢查結構
        if not self.check_skill_structure():
            all_passed = False

        # 4. 檢查重複名稱
        if not self.check_duplicate_names():
            all_passed = False

        # 5. 模擬載入檢查
        if not self.check_claude_code_load():
            all_passed = False

        # 6. 生成報告
        self.generate_report()

        return all_passed

def main():
    checker = HealthChecker()
    success = checker.run()

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
