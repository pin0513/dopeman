#!/usr/bin/env python3
"""
DopeMAN - Integrity Checker
完整性檢查工具：檢查 Skills/Rules/Agents/Commands 的完整性
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import yaml

# 路徑配置
HOME = Path.home()
CLAUDE_DIR = HOME / ".claude"
AGENT_PROJECTS_DIR = HOME / "AgentProjects"
MEMORY_DIR = CLAUDE_DIR / "memory" / "dopeman"

# 有效的 model 值
VALID_MODELS = {"opus", "sonnet", "haiku"}

class IntegrityChecker:
    def __init__(self):
        self.report = {
            "version": "1.0.0",
            "scan_time": datetime.now().isoformat(),
            "summary": {
                "total_items": 0,
                "ok": 0,
                "warning": 0,
                "error": 0
            },
            "skills": {"count": 0, "ok": 0, "issues": []},
            "rules": {"count": 0, "ok": 0, "issues": []},
            "agents": {"count": 0, "ok": 0, "issues": []},
            "commands": {"count": 0, "ok": 0, "issues": []},
            "symlinks": {"count": 0, "broken": 0, "issues": []}
        }

    def extract_yaml_frontmatter(self, file_path: Path) -> Optional[Dict]:
        """提取 YAML frontmatter"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # 檢查是否以 --- 開頭
            if not content.startswith('---\n'):
                return None

            # 找到第二個 ---
            parts = content.split('---\n', 2)
            if len(parts) < 3:
                return None

            yaml_content = parts[1]
            return yaml.safe_load(yaml_content)
        except Exception as e:
            return None

    def check_skills(self, check_type: str = "all"):
        """檢查 Skills"""
        skills_dirs = []

        # 1. 全域 Skills
        if CLAUDE_DIR.exists():
            global_skills = CLAUDE_DIR / "skills"
            if global_skills.exists():
                for item in global_skills.iterdir():
                    if item.is_dir():
                        skills_dirs.append(("global", item))
                    elif item.is_symlink():
                        skills_dirs.append(("global_symlink", item))

        # 2. 專案 Skills
        if AGENT_PROJECTS_DIR.exists():
            for project_dir in AGENT_PROJECTS_DIR.iterdir():
                if not project_dir.is_dir():
                    continue

                skills_dir = project_dir / ".claude" / "skills"
                if skills_dir.exists():
                    for skill_dir in skills_dir.iterdir():
                        if skill_dir.is_dir():
                            skills_dirs.append(("project", skill_dir))

        # 檢查每個 Skill
        for skill_type, skill_path in skills_dirs:
            self.report["skills"]["count"] += 1

            # 如果是 symlink，檢查目標有效性
            if skill_path.is_symlink():
                self.report["symlinks"]["count"] += 1
                target = skill_path.resolve()

                if not target.exists():
                    self.report["symlinks"]["broken"] += 1
                    self.report["symlinks"]["issues"].append({
                        "path": str(skill_path),
                        "issue": "broken_symlink",
                        "message": f"Symlink 目標不存在: {target}"
                    })
                    self.report["summary"]["error"] += 1
                    continue

                # 更新路徑為實際目標
                skill_path = target

            # 檢查 SKILL.md
            skill_md = skill_path / "SKILL.md"
            if not skill_md.exists():
                self.report["skills"]["issues"].append({
                    "path": str(skill_path),
                    "issue": "missing_skill_md",
                    "message": "缺少 SKILL.md 檔案"
                })
                self.report["summary"]["error"] += 1
                continue

            # 檢查 YAML frontmatter
            frontmatter = self.extract_yaml_frontmatter(skill_md)
            if not frontmatter:
                self.report["skills"]["issues"].append({
                    "path": str(skill_md),
                    "issue": "missing_frontmatter",
                    "message": "缺少 YAML frontmatter"
                })
                self.report["summary"]["error"] += 1
                continue

            # 檢查必要欄位
            required_fields = ["name", "description"]
            missing_fields = [f for f in required_fields if f not in frontmatter]

            if missing_fields:
                self.report["skills"]["issues"].append({
                    "path": str(skill_md),
                    "issue": "incomplete_frontmatter",
                    "message": f"缺少必要欄位: {', '.join(missing_fields)}"
                })
                self.report["summary"]["warning"] += 1
            else:
                self.report["skills"]["ok"] += 1
                self.report["summary"]["ok"] += 1

    def check_rules(self):
        """檢查 Rules"""
        rules_dirs = []

        # 1. 全域 Rules
        global_rules = CLAUDE_DIR / "rules"
        if global_rules.exists():
            for rule_file in global_rules.glob("*.md"):
                rules_dirs.append(("global", rule_file))

        # 2. 專案 Rules
        if AGENT_PROJECTS_DIR.exists():
            for project_dir in AGENT_PROJECTS_DIR.iterdir():
                if not project_dir.is_dir():
                    continue

                rules_dir = project_dir / ".claude" / "rules"
                if rules_dir.exists():
                    for rule_file in rules_dir.glob("*.md"):
                        rules_dirs.append(("project", rule_file))

        # 檢查每個 Rule
        for rule_type, rule_path in rules_dirs:
            self.report["rules"]["count"] += 1

            # 檢查 YAML frontmatter
            frontmatter = self.extract_yaml_frontmatter(rule_path)
            if not frontmatter:
                self.report["rules"]["issues"].append({
                    "path": str(rule_path),
                    "issue": "missing_frontmatter",
                    "message": "缺少 YAML frontmatter"
                })
                self.report["summary"]["error"] += 1
                continue

            # 檢查必要欄位
            required_fields = ["name", "description"]
            missing_fields = [f for f in required_fields if f not in frontmatter]

            if missing_fields:
                self.report["rules"]["issues"].append({
                    "path": str(rule_path),
                    "issue": "incomplete_frontmatter",
                    "message": f"缺少必要欄位: {', '.join(missing_fields)}"
                })
                self.report["summary"]["warning"] += 1
                continue

            # 檢查內容結構
            content = rule_path.read_text(encoding='utf-8')

            if "## Rule Content" not in content:
                self.report["rules"]["issues"].append({
                    "path": str(rule_path),
                    "issue": "missing_rule_content",
                    "message": "缺少 '## Rule Content' 區塊"
                })
                self.report["summary"]["warning"] += 1

            if "## Violation Determination" not in content:
                self.report["rules"]["issues"].append({
                    "path": str(rule_path),
                    "issue": "missing_violation",
                    "message": "缺少 '## Violation Determination' 區塊"
                })
                self.report["summary"]["warning"] += 1

            # 檢查檔案命名（應該是 kebab-case）
            if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*\.md$', rule_path.name):
                self.report["rules"]["issues"].append({
                    "path": str(rule_path),
                    "issue": "invalid_filename",
                    "message": f"檔案命名不符合 kebab-case: {rule_path.name}"
                })
                self.report["summary"]["warning"] += 1

            # 如果沒有問題
            if not any(issue["path"] == str(rule_path) for issue in self.report["rules"]["issues"]):
                self.report["rules"]["ok"] += 1
                self.report["summary"]["ok"] += 1

    def check_agents(self):
        """檢查 Agents"""
        agents_files = []

        # 掃描所有專案的 agents
        if AGENT_PROJECTS_DIR.exists():
            for project_dir in AGENT_PROJECTS_DIR.iterdir():
                if not project_dir.is_dir():
                    continue

                agents_dir = project_dir / ".claude" / "agents"
                if agents_dir.exists():
                    # 掃描所有 .md 檔案
                    for agent_file in agents_dir.rglob("*.md"):
                        agents_files.append((project_dir.name, agent_file, agents_dir))

        # 檢查每個 Agent
        for project_name, agent_path, agents_root in agents_files:
            self.report["agents"]["count"] += 1

            # 檢查 YAML frontmatter
            frontmatter = self.extract_yaml_frontmatter(agent_path)
            if not frontmatter:
                self.report["agents"]["issues"].append({
                    "path": str(agent_path),
                    "issue": "missing_frontmatter",
                    "message": "缺少 YAML frontmatter"
                })
                self.report["summary"]["error"] += 1
                continue

            # 檢查必要欄位
            required_fields = ["name", "description", "model"]
            missing_fields = [f for f in required_fields if f not in frontmatter]

            if missing_fields:
                self.report["agents"]["issues"].append({
                    "path": str(agent_path),
                    "issue": "incomplete_frontmatter",
                    "message": f"缺少必要欄位: {', '.join(missing_fields)}"
                })
                self.report["summary"]["warning"] += 1
                continue

            # 檢查 model 值有效性
            if frontmatter.get("model") not in VALID_MODELS:
                self.report["agents"]["issues"].append({
                    "path": str(agent_path),
                    "issue": "invalid_model",
                    "message": f"無效的 model 值: {frontmatter.get('model')} (應為 {', '.join(VALID_MODELS)})"
                })
                self.report["summary"]["error"] += 1
                continue

            # 檢查位置規則：Coordinator 應在根目錄，Workers 應在子目錄
            relative_path = agent_path.relative_to(agents_root)
            is_in_root = len(relative_path.parts) == 1

            agent_name = frontmatter.get("name", "").lower()
            is_coordinator = "coordinator" in agent_name or "coord" in agent_name

            if is_coordinator and not is_in_root:
                self.report["agents"]["issues"].append({
                    "path": str(agent_path),
                    "issue": "coordinator_location",
                    "message": "Coordinator 應該在 agents/ 根目錄"
                })
                self.report["summary"]["warning"] += 1

            # 如果沒有問題
            if not any(issue["path"] == str(agent_path) for issue in self.report["agents"]["issues"]):
                self.report["agents"]["ok"] += 1
                self.report["summary"]["ok"] += 1

    def check_commands(self):
        """檢查 Commands"""
        if not AGENT_PROJECTS_DIR.exists():
            return

        for project_dir in AGENT_PROJECTS_DIR.iterdir():
            if not project_dir.is_dir():
                continue

            commands_dir = project_dir / "commands"
            if not commands_dir.exists():
                continue

            for cmd_file in commands_dir.iterdir():
                if cmd_file.is_dir() or cmd_file.suffix in [".md", ".json", ".log", ".pid", ".html"]:
                    continue

                self.report["commands"]["count"] += 1

                # 檢查是否可執行
                if not os.access(cmd_file, os.X_OK):
                    self.report["commands"]["issues"].append({
                        "path": str(cmd_file),
                        "issue": "not_executable",
                        "message": "檔案不可執行 (缺少 chmod +x)"
                    })
                    self.report["summary"]["warning"] += 1
                    continue

                # 檢查 shebang
                try:
                    with open(cmd_file, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()

                        if not first_line.startswith('#!'):
                            self.report["commands"]["issues"].append({
                                "path": str(cmd_file),
                                "issue": "missing_shebang",
                                "message": "缺少 shebang (#!)"
                            })
                            self.report["summary"]["warning"] += 1
                        elif first_line not in [
                            "#!/usr/bin/env python3",
                            "#!/bin/bash",
                            "#!/usr/bin/env bash",
                            "#!/bin/sh"
                        ]:
                            self.report["commands"]["issues"].append({
                                "path": str(cmd_file),
                                "issue": "invalid_shebang",
                                "message": f"非標準 shebang: {first_line}"
                            })
                            self.report["summary"]["warning"] += 1
                except Exception as e:
                    self.report["commands"]["issues"].append({
                        "path": str(cmd_file),
                        "issue": "read_error",
                        "message": f"無法讀取檔案: {e}"
                    })
                    self.report["summary"]["error"] += 1
                    continue

                # 如果沒有問題
                if not any(issue["path"] == str(cmd_file) for issue in self.report["commands"]["issues"]):
                    self.report["commands"]["ok"] += 1
                    self.report["summary"]["ok"] += 1

    def update_summary(self):
        """更新摘要"""
        self.report["summary"]["total_items"] = (
            self.report["skills"]["count"] +
            self.report["rules"]["count"] +
            self.report["agents"]["count"] +
            self.report["commands"]["count"]
        )

    def save_report(self):
        """儲存報告"""
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        report_file = MEMORY_DIR / "integrity-report.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)

        return report_file

    def print_report(self, verbose: bool = False):
        """列印報告"""
        print("🔍 DopeMAN - 完整性檢查")
        print("━" * 50)
        print()

        # Skills
        print("📦 檢查 Skills...")
        print(f"   ✅ 總計: {self.report['skills']['count']} 個")
        print(f"   ✅ 正常: {self.report['skills']['ok']} 個")
        if self.report['skills']['issues']:
            print(f"   ⚠️  問題: {len(self.report['skills']['issues'])} 個")
            if verbose:
                for issue in self.report['skills']['issues']:
                    print(f"      - {issue['message']}")
                    print(f"        路徑: {issue['path']}")
        print()

        # Rules
        print("📋 檢查 Rules...")
        print(f"   ✅ 總計: {self.report['rules']['count']} 個")
        print(f"   ✅ 正常: {self.report['rules']['ok']} 個")
        if self.report['rules']['issues']:
            print(f"   ⚠️  問題: {len(self.report['rules']['issues'])} 個")
            if verbose:
                for issue in self.report['rules']['issues']:
                    print(f"      - {issue['message']}")
                    print(f"        路徑: {issue['path']}")
        print()

        # Agents
        print("🤖 檢查 Agents...")
        print(f"   ✅ 總計: {self.report['agents']['count']} 個")
        print(f"   ✅ 正常: {self.report['agents']['ok']} 個")
        if self.report['agents']['issues']:
            print(f"   ⚠️  問題: {len(self.report['agents']['issues'])} 個")
            if verbose:
                for issue in self.report['agents']['issues']:
                    print(f"      - {issue['message']}")
                    print(f"        路徑: {issue['path']}")
        print()

        # Commands
        print("⚙️  檢查 Commands...")
        print(f"   ✅ 總計: {self.report['commands']['count']} 個")
        print(f"   ✅ 正常: {self.report['commands']['ok']} 個")
        if self.report['commands']['issues']:
            print(f"   ⚠️  問題: {len(self.report['commands']['issues'])} 個")
            if verbose:
                for issue in self.report['commands']['issues']:
                    print(f"      - {issue['message']}")
                    print(f"        路徑: {issue['path']}")
        print()

        # Symlinks
        if self.report['symlinks']['count'] > 0:
            print("🔗 檢查 Symlinks...")
            print(f"   ✅ 總計: {self.report['symlinks']['count']} 個")
            print(f"   ❌ 損壞: {self.report['symlinks']['broken']} 個")
            if self.report['symlinks']['issues']:
                if verbose:
                    for issue in self.report['symlinks']['issues']:
                        print(f"      - {issue['message']}")
                        print(f"        路徑: {issue['path']}")
            print()

        # 摘要
        print("━" * 50)
        print("📊 摘要：")
        print(f"   總計檢查: {self.report['summary']['total_items']} 項")
        print(f"   正常: {self.report['summary']['ok']} 項")
        print(f"   警告: {self.report['summary']['warning']} 項")
        print(f"   錯誤: {self.report['summary']['error']} 項")
        print()

        if self.report['summary']['warning'] > 0 or self.report['summary']['error'] > 0:
            print("💡 建議執行: /dopeman fix 來自動修復問題")
        else:
            print("✅ 所有檢查項目都正常！")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='DopeMAN - 完整性檢查工具')
    parser.add_argument('--type', choices=['skills', 'rules', 'agents', 'commands', 'all'],
                        default='all', help='檢查類型')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細輸出')
    parser.add_argument('--save', action='store_true', help='儲存報告到 JSON')

    args = parser.parse_args()

    checker = IntegrityChecker()

    # 執行檢查
    if args.type in ['skills', 'all']:
        checker.check_skills()

    if args.type in ['rules', 'all']:
        checker.check_rules()

    if args.type in ['agents', 'all']:
        checker.check_agents()

    if args.type in ['commands', 'all']:
        checker.check_commands()

    # 更新摘要
    checker.update_summary()

    # 列印報告
    checker.print_report(verbose=args.verbose)

    # 儲存報告
    if args.save or args.type == 'all':
        report_file = checker.save_report()
        print(f"📄 報告已儲存: {report_file}")

    # 回傳狀態碼
    if checker.report['summary']['error'] > 0:
        sys.exit(1)
    elif checker.report['summary']['warning'] > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
