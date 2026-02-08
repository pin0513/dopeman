#!/usr/bin/env python3
"""
DopeMAN - Skills Auto-Linking Tool
自動掃描並建立 Skills 的全域連結，分類為：
1. 全域通用能力
2. 專業指定能力
3. 專屬能力
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Set

# 路徑配置
HOME = Path.home()
CLAUDE_SKILLS_DIR = HOME / ".claude" / "skills"
DEV_DIR = HOME / "DEV"
AGENT_PROJECTS_DIR = HOME / "AgentProjects"

# Skills 分類規則
UNIVERSAL_SKILLS = {
    "team-maker", "dopeman", "team-deployment", "team-topology-analysis",
    "granularity-calibration", "quality-validation", "role-decomposition",
    "structured-interview", "prompt-optimization", "md-generation-standard"
}

PROFESSIONAL_PREFIXES = {
    "dev-team": "開發團隊",
    "slide": "簡報製作",
    "article": "內容撰寫",
    "web-produce": "網站製作",
    "mayo": "MAYO 專屬",
    "ado": "Azure DevOps",
}

class SkillLinker:
    def __init__(self):
        self.universal = []      # 全域通用能力
        self.professional = {}   # 專業指定能力 {category: [skills]}
        self.exclusive = []      # 專屬能力
        self.existing = set()    # 已存在的 symlinks

    def scan_existing_links(self):
        """掃描已存在的 symlinks"""
        if not CLAUDE_SKILLS_DIR.exists():
            CLAUDE_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
            return

        for item in CLAUDE_SKILLS_DIR.iterdir():
            if item.is_symlink():
                self.existing.add(item.name)

    def classify_skill(self, skill_path: Path) -> str:
        """分類 Skill"""
        skill_name = skill_path.name

        # 全域通用能力
        if skill_name in UNIVERSAL_SKILLS:
            return "universal"

        # 專業指定能力
        for prefix, category in PROFESSIONAL_PREFIXES.items():
            if skill_name.startswith(prefix):
                return f"professional:{category}"

        # 專屬能力
        return "exclusive"

    def scan_skills(self):
        """掃描所有 Skills"""
        skills_found = []

        # 1. 掃描 AgentProjects
        if AGENT_PROJECTS_DIR.exists():
            for project_dir in AGENT_PROJECTS_DIR.iterdir():
                if not project_dir.is_dir():
                    continue

                # 檢查根目錄的 SKILL.md
                if (project_dir / "SKILL.md").exists():
                    skills_found.append(project_dir)

                # 檢查 .claude/skills/
                skills_dir = project_dir / ".claude" / "skills"
                if skills_dir.exists():
                    for skill_dir in skills_dir.iterdir():
                        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                            skills_found.append(skill_dir)

        # 2. 掃描 DEV 目錄
        if DEV_DIR.exists():
            for project_dir in DEV_DIR.rglob(".claude/skills"):
                for skill_dir in project_dir.iterdir():
                    if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                        skills_found.append(skill_dir)

        return skills_found

    def categorize_skills(self, skills: List[Path]):
        """分類 Skills"""
        for skill_path in skills:
            skill_name = skill_path.name

            # 跳過已存在的
            if skill_name in self.existing:
                continue

            classification = self.classify_skill(skill_path)

            if classification == "universal":
                self.universal.append(skill_path)
            elif classification.startswith("professional:"):
                category = classification.split(":", 1)[1]
                if category not in self.professional:
                    self.professional[category] = []
                self.professional[category].append(skill_path)
            else:
                self.exclusive.append(skill_path)

    def create_links(self, dry_run=False):
        """建立 symlinks"""
        created = []

        def create_link(skill_path: Path):
            link_path = CLAUDE_SKILLS_DIR / skill_path.name
            if not dry_run:
                try:
                    link_path.symlink_to(skill_path)
                    created.append(skill_path.name)
                    return True
                except Exception as e:
                    print(f"   ❌ 建立失敗: {skill_path.name} - {e}")
                    return False
            else:
                created.append(skill_path.name)
                return True

        # 1. 全域通用能力
        if self.universal:
            print("\n📦 全域通用能力")
            print("=" * 50)
            for skill_path in self.universal:
                if create_link(skill_path):
                    print(f"   ✅ {skill_path.name}")

        # 2. 專業指定能力
        if self.professional:
            print("\n🎯 專業指定能力")
            print("=" * 50)
            for category, skills in sorted(self.professional.items()):
                print(f"\n   【{category}】")
                for skill_path in skills:
                    if create_link(skill_path):
                        print(f"      ✅ {skill_path.name}")

        # 3. 專屬能力
        if self.exclusive:
            print("\n🔒 專屬能力")
            print("=" * 50)
            for skill_path in self.exclusive:
                if create_link(skill_path):
                    print(f"   ✅ {skill_path.name}")

        return created

    def generate_report(self):
        """生成報告"""
        total = len(self.universal) + sum(len(s) for s in self.professional.values()) + len(self.exclusive)

        print("\n" + "=" * 50)
        print("📊 掃描摘要")
        print("=" * 50)
        print(f"   全域通用能力: {len(self.universal)} 個")
        print(f"   專業指定能力: {sum(len(s) for s in self.professional.values())} 個")
        for category, skills in sorted(self.professional.items()):
            print(f"      - {category}: {len(skills)} 個")
        print(f"   專屬能力: {len(self.exclusive)} 個")
        print(f"   已存在連結: {len(self.existing)} 個")
        print(f"   \n   總計發現: {total} 個新 Skills")

def main():
    import sys

    dry_run = "--dry-run" in sys.argv

    print("🔍 DopeMAN - Skills Auto-Linking")
    print("=" * 50)

    linker = SkillLinker()

    # 1. 掃描已存在的 links
    print("\n⏳ 掃描已存在的連結...")
    linker.scan_existing_links()
    print(f"   已存在: {len(linker.existing)} 個")

    # 2. 掃描所有 Skills
    print("\n⏳ 掃描所有 Skills...")
    skills = linker.scan_skills()
    print(f"   發現: {len(skills)} 個 Skills")

    # 3. 分類
    print("\n⏳ 分類 Skills...")
    linker.categorize_skills(skills)

    # 4. 生成報告
    linker.generate_report()

    # 5. 建立連結
    if dry_run:
        print("\n🔍 Dry-run 模式（不實際建立連結）")

    created = linker.create_links(dry_run=dry_run)

    print("\n" + "=" * 50)
    if dry_run:
        print(f"✅ Dry-run 完成！預計建立 {len(created)} 個連結")
        print("\n💡 執行 `python link-skills.py` 來實際建立連結")
    else:
        print(f"✅ 完成！成功建立 {len(created)} 個連結")
        print("\n💡 現在可以使用這些 skills 了！")
    print("=" * 50)

if __name__ == "__main__":
    main()
