#!/usr/bin/env python3
"""
DopeMAN - Auto Fix Tool
自動修復工具：修復損壞的 symlinks、補齊缺少的 YAML frontmatter
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import yaml

# 路徑配置
HOME = Path.home()
CLAUDE_DIR = HOME / ".claude"
AGENT_PROJECTS_DIR = HOME / "AgentProjects"
MEMORY_DIR = CLAUDE_DIR / "memory" / "dopeman"
BACKUP_DIR = MEMORY_DIR / ".backup"

# 有效的 model 值
VALID_MODELS = {"opus", "sonnet", "haiku"}


class AutoFixer:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.backup_dir = None
        self.fix_history = {
            "version": "1.0.0",
            "fix_time": datetime.now().isoformat(),
            "dry_run": dry_run,
            "fixes": {
                "symlinks_removed": [],
                "symlinks_rebuilt": [],
                "frontmatter_added": [],
                "frontmatter_fixed": [],
                "permissions_fixed": []
            },
            "summary": {
                "total_fixes": 0,
                "successful": 0,
                "failed": 0
            }
        }

    def create_backup(self):
        """建立備份"""
        if self.dry_run:
            print("🔍 Dry-run 模式：跳過備份")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.backup_dir = BACKUP_DIR / timestamp
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        print(f"✅ 備份已建立: {self.backup_dir}")

    def backup_file(self, file_path: Path):
        """備份單個檔案"""
        if self.dry_run or not self.backup_dir:
            return

        try:
            relative_path = file_path.relative_to(HOME)
            backup_path = self.backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            if file_path.is_symlink():
                # 如果是 symlink，記錄目標
                target = os.readlink(file_path)
                with open(backup_path.with_suffix('.symlink'), 'w') as f:
                    f.write(target)
            else:
                shutil.copy2(file_path, backup_path)
        except Exception as e:
            print(f"   ⚠️  備份失敗: {file_path} - {e}")

    def extract_yaml_frontmatter(self, file_path: Path) -> Optional[Dict]:
        """提取 YAML frontmatter"""
        try:
            content = file_path.read_text(encoding='utf-8')

            if not content.startswith('---\n'):
                return None

            parts = content.split('---\n', 2)
            if len(parts) < 3:
                return None

            yaml_content = parts[1]
            return yaml.safe_load(yaml_content)
        except Exception:
            return None

    def add_yaml_frontmatter(self, file_path: Path, frontmatter: Dict):
        """新增 YAML frontmatter"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # 產生 YAML frontmatter
            yaml_str = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
            new_content = f"---\n{yaml_str}---\n\n{content}"

            if not self.dry_run:
                self.backup_file(file_path)
                file_path.write_text(new_content, encoding='utf-8')

            return True
        except Exception as e:
            print(f"   ❌ 新增失敗: {file_path} - {e}")
            return False

    def fix_broken_symlinks(self):
        """修復損壞的 symlinks"""
        print("🔗 修復損壞的 Symlinks...")

        if not CLAUDE_DIR.exists():
            return

        skills_dir = CLAUDE_DIR / "skills"
        if not skills_dir.exists():
            return

        for item in skills_dir.iterdir():
            if not item.is_symlink():
                continue

            try:
                target = item.resolve(strict=True)
                # symlink 正常，跳過
                continue
            except Exception:
                # symlink 損壞
                self.fix_history["fixes"]["total_fixes"] += 1

                # 嘗試尋找新位置
                skill_name = item.name
                found = False

                # 搜尋 AgentProjects
                if AGENT_PROJECTS_DIR.exists():
                    for project_dir in AGENT_PROJECTS_DIR.iterdir():
                        if not project_dir.is_dir():
                            continue

                        # 檢查專案根目錄
                        if project_dir.name == skill_name and (project_dir / "SKILL.md").exists():
                            if not self.dry_run:
                                self.backup_file(item)
                                item.unlink()
                                item.symlink_to(project_dir)

                            self.fix_history["fixes"]["symlinks_rebuilt"].append({
                                "link": str(item),
                                "old_target": "unknown",
                                "new_target": str(project_dir)
                            })
                            self.fix_history["summary"]["successful"] += 1
                            print(f"   ✅ 重建: {skill_name} → {project_dir}")
                            found = True
                            break

                        # 檢查 .claude/skills/
                        skills_search = project_dir / ".claude" / "skills" / skill_name
                        if skills_search.exists() and (skills_search / "SKILL.md").exists():
                            if not self.dry_run:
                                self.backup_file(item)
                                item.unlink()
                                item.symlink_to(skills_search)

                            self.fix_history["fixes"]["symlinks_rebuilt"].append({
                                "link": str(item),
                                "old_target": "unknown",
                                "new_target": str(skills_search)
                            })
                            self.fix_history["summary"]["successful"] += 1
                            print(f"   ✅ 重建: {skill_name} → {skills_search}")
                            found = True
                            break

                if not found:
                    # 找不到新位置，移除損壞的 symlink
                    if not self.dry_run:
                        self.backup_file(item)
                        item.unlink()

                    self.fix_history["fixes"]["symlinks_removed"].append({
                        "link": str(item),
                        "reason": "目標已不存在"
                    })
                    self.fix_history["summary"]["successful"] += 1
                    print(f"   ✅ 移除: {skill_name} (目標已不存在)")

    def fix_missing_frontmatter(self):
        """修復缺少的 frontmatter"""
        print("\n📝 修復缺少的 YAML Frontmatter...")

        fixed_count = 0

        # 1. 修復 Skills
        if CLAUDE_DIR.exists():
            skills_dirs = []

            # 全域 Skills
            global_skills = CLAUDE_DIR / "skills"
            if global_skills.exists():
                for skill_dir in global_skills.iterdir():
                    if skill_dir.is_dir():
                        skills_dirs.append(skill_dir)

            # 專案 Skills
            if AGENT_PROJECTS_DIR.exists():
                for project_dir in AGENT_PROJECTS_DIR.iterdir():
                    if not project_dir.is_dir():
                        continue

                    skills_dir = project_dir / ".claude" / "skills"
                    if skills_dir.exists():
                        for skill_dir in skills_dir.iterdir():
                            if skill_dir.is_dir():
                                skills_dirs.append(skill_dir)

            for skill_dir in skills_dirs:
                skill_md = skill_dir / "SKILL.md"
                if not skill_md.exists():
                    continue

                frontmatter = self.extract_yaml_frontmatter(skill_md)
                if frontmatter is None:
                    # 缺少 frontmatter
                    new_frontmatter = {
                        "name": skill_dir.name.replace('-', ' ').title(),
                        "description": "TODO: Add description"
                    }

                    if self.add_yaml_frontmatter(skill_md, new_frontmatter):
                        self.fix_history["fixes"]["frontmatter_added"].append({
                            "path": str(skill_md),
                            "type": "skill"
                        })
                        self.fix_history["summary"]["successful"] += 1
                        print(f"   ✅ 新增 frontmatter: {skill_md.name}")
                        fixed_count += 1

        # 2. 修復 Agents
        if AGENT_PROJECTS_DIR.exists():
            for project_dir in AGENT_PROJECTS_DIR.iterdir():
                if not project_dir.is_dir():
                    continue

                agents_dir = project_dir / ".claude" / "agents"
                if not agents_dir.exists():
                    continue

                for agent_file in agents_dir.rglob("*.md"):
                    frontmatter = self.extract_yaml_frontmatter(agent_file)

                    if frontmatter is None:
                        # 缺少 frontmatter
                        agent_name = agent_file.stem.replace('-', ' ').title()
                        new_frontmatter = {
                            "name": agent_name,
                            "description": "TODO: Add description",
                            "model": "sonnet"
                        }

                        if self.add_yaml_frontmatter(agent_file, new_frontmatter):
                            self.fix_history["fixes"]["frontmatter_added"].append({
                                "path": str(agent_file),
                                "type": "agent"
                            })
                            self.fix_history["summary"]["successful"] += 1
                            print(f"   ✅ 新增 frontmatter: {agent_file.name}")
                            fixed_count += 1

                    elif frontmatter:
                        # 檢查並修復不完整的 frontmatter
                        needs_fix = False
                        if "model" not in frontmatter:
                            frontmatter["model"] = "sonnet"
                            needs_fix = True

                        if frontmatter.get("model") not in VALID_MODELS:
                            frontmatter["model"] = "sonnet"
                            needs_fix = True

                        if needs_fix:
                            # 重寫整個檔案
                            content = agent_file.read_text(encoding='utf-8')
                            parts = content.split('---\n', 2)
                            if len(parts) >= 3:
                                yaml_str = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
                                new_content = f"---\n{yaml_str}---\n{parts[2]}"

                                if not self.dry_run:
                                    self.backup_file(agent_file)
                                    agent_file.write_text(new_content, encoding='utf-8')

                                self.fix_history["fixes"]["frontmatter_fixed"].append({
                                    "path": str(agent_file),
                                    "type": "agent"
                                })
                                self.fix_history["summary"]["successful"] += 1
                                print(f"   ✅ 修復 frontmatter: {agent_file.name}")
                                fixed_count += 1

        if fixed_count == 0:
            print("   ℹ️  沒有需要修復的 frontmatter")

    def fix_command_permissions(self):
        """修復 Command 權限"""
        print("\n⚙️  修復 Command 權限...")

        fixed_count = 0

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

                # 檢查是否可執行
                if not os.access(cmd_file, os.X_OK):
                    if not self.dry_run:
                        os.chmod(cmd_file, 0o755)

                    self.fix_history["fixes"]["permissions_fixed"].append({
                        "path": str(cmd_file)
                    })
                    self.fix_history["summary"]["successful"] += 1
                    print(f"   ✅ 設定執行權限: {cmd_file.name}")
                    fixed_count += 1

        if fixed_count == 0:
            print("   ℹ️  所有 commands 權限正常")

    def save_history(self):
        """儲存修復歷史"""
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        history_file = MEMORY_DIR / "fix-history.json"

        # 讀取舊歷史
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    old_history = json.load(f)
                    if "history" not in old_history:
                        old_history = {"history": []}
            except Exception:
                old_history = {"history": []}
        else:
            old_history = {"history": []}

        # 加入新紀錄
        old_history["history"].append(self.fix_history)

        # 只保留最近 50 次
        old_history["history"] = old_history["history"][-50:]

        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(old_history, f, indent=2, ensure_ascii=False)

        return history_file

    def print_summary(self):
        """列印摘要"""
        print("\n" + "━" * 50)
        print("📊 修復摘要：")
        print(f"   損壞的 Symlinks:")
        print(f"      移除: {len(self.fix_history['fixes']['symlinks_removed'])} 個")
        print(f"      重建: {len(self.fix_history['fixes']['symlinks_rebuilt'])} 個")
        print(f"   Frontmatter:")
        print(f"      新增: {len(self.fix_history['fixes']['frontmatter_added'])} 個")
        print(f"      修復: {len(self.fix_history['fixes']['frontmatter_fixed'])} 個")
        print(f"   權限修復: {len(self.fix_history['fixes']['permissions_fixed'])} 個")
        print()
        print(f"   總計修復: {self.fix_history['summary']['successful']} 項")

        if self.backup_dir and not self.dry_run:
            print(f"\n✅ 備份位置: {self.backup_dir}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='DopeMAN - 自動修復工具')
    parser.add_argument('--dry-run', action='store_true', help='預覽模式（不實際執行）')
    parser.add_argument('--save', action='store_true', help='儲存修復歷史')

    args = parser.parse_args()

    print("🔧 DopeMAN - 自動修復")
    print("━" * 50)
    print()

    if args.dry_run:
        print("🔍 Dry-run 模式（預覽修復動作）")
        print()

    fixer = AutoFixer(dry_run=args.dry_run)

    # 建立備份
    fixer.create_backup()
    print()

    # 執行修復
    fixer.fix_broken_symlinks()
    fixer.fix_missing_frontmatter()
    fixer.fix_command_permissions()

    # 列印摘要
    fixer.print_summary()

    # 儲存歷史
    if args.save or not args.dry_run:
        history_file = fixer.save_history()
        print(f"\n📄 修復歷史已儲存: {history_file}")

    print()
    print("━" * 50)

    if args.dry_run:
        print("🔍 Dry-run 完成！執行 `python fix.py` 來實際修復")
    else:
        print("✅ 修復完成！")

    print("━" * 50)


if __name__ == "__main__":
    main()
