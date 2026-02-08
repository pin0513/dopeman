#!/usr/bin/env python3
"""
Skills Control Center - Real Data Scanner
掃描真實的 Skills, Agents, Rules, Commands 並生成資料結構
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# 路徑配置
HOME = Path.home()
CLAUDE_DIR = HOME / ".claude"
DEV_DIR = HOME / "DEV"

class RealDataScanner:
    def __init__(self):
        self.data = {
            "version": "1.0.0",
            "last_scan": datetime.now().isoformat(),
            "categories": {
                "global_skills": {"count": 0, "items": []},
                "project_skills": {"count": 0, "items": []},
                "dev_skills": {"count": 0, "items": []},
                "dev_projects": {"count": 0, "items": []},
                "global_rules": {"count": 0, "items": []},
                "project_rules": {"count": 0, "items": []},
                "agents": {"count": 0, "items": []},
                "commands": {"count": 0, "items": []}
            },
            "relationships": {
                "skill_to_agents": {},
                "agent_to_skills": {},
                "agent_to_rules": {},
                "command_to_skill": {}
            },
            "layers": {
                "entry": {"skills": [], "commands": []},
                "coordination": {"coordinators": []},
                "execution": {"workers": [], "sub_skills": []},
            }
        }

    def scan_global_skills(self):
        """掃描全域 Skills"""
        skills_dir = CLAUDE_DIR / "skills"
        if not skills_dir.exists():
            return

        for skill_path in skills_dir.rglob("SKILL.md"):
            # 排除 node_modules
            if "node_modules" in str(skill_path):
                continue

            skill_name = skill_path.parent.name

            # 讀取 YAML frontmatter
            content = skill_path.read_text(encoding='utf-8')
            frontmatter = self.extract_frontmatter(content)

            # 判斷是否為 team skill (有 .claude/agents/)
            has_agents = (skill_path.parent / ".claude" / "agents").exists()

            skill_info = {
                "name": skill_name,
                "path": str(skill_path.parent.relative_to(HOME)),
                "type": "team" if has_agents else "single",
                "description": frontmatter.get("description", ""),
                "source": "local",
                "has_agents": has_agents,
                "has_git": (skill_path.parent / ".git").exists()
            }

            self.data["categories"]["global_skills"]["items"].append(skill_info)

            # 如果是 team skill，加入 entry layer
            if has_agents:
                self.data["layers"]["entry"]["skills"].append(skill_name)

        self.data["categories"]["global_skills"]["count"] = len(
            self.data["categories"]["global_skills"]["items"]
        )

    def scan_project_skills(self):
        """掃描專案 Skills"""
        # 掃描 DEV 目錄下的專案
        for claude_dir in DEV_DIR.rglob(".claude"):
            # 排除 node_modules 和全域 .claude
            if "node_modules" in str(claude_dir) or str(claude_dir) == str(CLAUDE_DIR):
                continue

            project_path = claude_dir.parent
            skills_dir = claude_dir / "skills"

            if not skills_dir.exists():
                continue

            for skill_path in skills_dir.rglob("SKILL.md"):
                skill_name = skill_path.parent.name

                project_info = {
                    "project_path": str(project_path.relative_to(HOME)),
                    "skill_name": skill_name,
                    "skill_path": str(skill_path.parent.relative_to(project_path)),
                    "is_duplicate": self.is_global_skill(skill_name)
                }

                self.data["categories"]["project_skills"]["items"].append(project_info)

        self.data["categories"]["project_skills"]["count"] = len(
            self.data["categories"]["project_skills"]["items"]
        )

    def scan_dev_skills(self):
        """掃描開發中 Skills (有 .git 的)"""
        projects_dir = DEV_DIR / "projects"
        if not projects_dir.exists():
            return

        for project_dir in projects_dir.iterdir():
            if not project_dir.is_dir():
                continue

            git_dir = project_dir / ".git"
            if not git_dir.exists():
                continue

            # 檢查是否有 SKILL.md 或 .claude/
            has_skill = (project_dir / "SKILL.md").exists() or (project_dir / ".claude").exists()

            if has_skill:
                dev_info = {
                    "name": project_dir.name,
                    "path": str(project_dir.relative_to(HOME)),
                    "has_git": True,
                    "dirty": self.check_git_dirty(project_dir)
                }

                self.data["categories"]["dev_skills"]["items"].append(dev_info)

        self.data["categories"]["dev_skills"]["count"] = len(
            self.data["categories"]["dev_skills"]["items"]
        )

    def scan_global_rules(self):
        """掃描全域 Rules"""
        rules_dir = CLAUDE_DIR / "rules"
        if not rules_dir.exists():
            return

        for rule_path in rules_dir.glob("*.md"):
            content = rule_path.read_text(encoding='utf-8')
            frontmatter = self.extract_frontmatter(content)
            applicability = self.extract_applicability(content)

            rule_info = {
                "name": rule_path.stem,
                "path": str(rule_path.relative_to(HOME)),
                "description": frontmatter.get("description", ""),
                "applicability": applicability,
                "scope": "global"
            }

            self.data["categories"]["global_rules"]["items"].append(rule_info)

        self.data["categories"]["global_rules"]["count"] = len(
            self.data["categories"]["global_rules"]["items"]
        )

    def scan_project_rules(self):
        """掃描專案 Rules"""
        for claude_dir in DEV_DIR.rglob(".claude"):
            if "node_modules" in str(claude_dir) or str(claude_dir) == str(CLAUDE_DIR):
                continue

            project_path = claude_dir.parent
            rules_dir = claude_dir / "rules"

            if not rules_dir.exists():
                continue

            for rule_path in rules_dir.glob("*.md"):
                content = rule_path.read_text(encoding='utf-8')
                frontmatter = self.extract_frontmatter(content)
                applicability = self.extract_applicability(content)

                rule_info = {
                    "project_path": str(project_path.relative_to(HOME)),
                    "name": rule_path.stem,
                    "rule_path": str(rule_path.relative_to(project_path)),
                    "description": frontmatter.get("description", ""),
                    "applicability": applicability,
                    "scope": "project"
                }

                self.data["categories"]["project_rules"]["items"].append(rule_info)

        self.data["categories"]["project_rules"]["count"] = len(
            self.data["categories"]["project_rules"]["items"]
        )

    def scan_agents(self):
        """掃描 Agents"""
        # 掃描專案中的 agents
        for claude_dir in DEV_DIR.rglob(".claude"):
            if "node_modules" in str(claude_dir) or str(claude_dir) == str(CLAUDE_DIR):
                continue

            project_path = claude_dir.parent
            agents_dir = claude_dir / "agents"

            if not agents_dir.exists():
                continue

            # 找出 coordinator (在 agents 根目錄的 .md)
            for agent_path in agents_dir.glob("*.md"):
                agent_info = {
                    "name": agent_path.stem,
                    "path": str(agent_path.relative_to(HOME)),
                    "type": "coordinator",
                    "belongs_to_project": str(project_path.relative_to(HOME)),
                    "delegates_to": []
                }

                self.data["categories"]["agents"]["items"].append(agent_info)
                self.data["layers"]["coordination"]["coordinators"].append(agent_path.stem)

            # 找出 workers (在子目錄的 .md)
            for agent_path in agents_dir.rglob("*.md"):
                # 跳過已處理的 coordinator
                if agent_path.parent == agents_dir:
                    continue

                agent_info = {
                    "name": agent_path.stem,
                    "path": str(agent_path.relative_to(HOME)),
                    "type": "worker",
                    "group": agent_path.parent.name,
                    "belongs_to_project": str(project_path.relative_to(HOME))
                }

                self.data["categories"]["agents"]["items"].append(agent_info)
                self.data["layers"]["execution"]["workers"].append(agent_path.stem)

        self.data["categories"]["agents"]["count"] = len(
            self.data["categories"]["agents"]["items"]
        )

    def scan_commands(self):
        """掃描 Commands（從 SKILL.md 提取）"""
        # 簡化版：從 dopeman SKILL.md 提取
        dopeman_skill = CLAUDE_DIR / "skills" / "dopeman" / "SKILL.md"

        if dopeman_skill.exists():
            content = dopeman_skill.read_text(encoding='utf-8')

            # 提取命令表格
            commands = [
                {"name": "check-updates", "description": "檢查 skills 更新"},
                {"name": "organize", "description": "整理指定目錄"},
                {"name": "export-config", "description": "匯出環境配置"},
                {"name": "import-config", "description": "匯入環境配置"},
                {"name": "usage-report", "description": "產生使用報告"},
                {"name": "discover-skills", "description": "搜尋推薦的新 skills"},
                {"name": "health-check", "description": "完整環境健檢"},
                {"name": "control-center", "description": "Skills 總控台"}
            ]

            for cmd in commands:
                cmd_info = {
                    "name": cmd["name"],
                    "full_command": f"/dopeman {cmd['name']}",
                    "entry_skill": "dopeman",
                    "description": cmd["description"]
                }

                self.data["categories"]["commands"]["items"].append(cmd_info)
                self.data["layers"]["entry"]["commands"].append(cmd_info["full_command"])

        self.data["categories"]["commands"]["count"] = len(
            self.data["categories"]["commands"]["items"]
        )

    def scan_dev_projects(self):
        """掃描開發專案"""
        import subprocess

        # 掃描 ~/DEV 下所有有 .git 的專案（maxdepth 2）
        for git_dir in sorted(DEV_DIR.glob("*/.git")):
            project_dir = git_dir.parent
            project_name = project_dir.name

            # 取得 Git remote URL
            remote_url = ""
            try:
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=project_dir,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    remote_url = result.stdout.strip()
            except:
                pass

            # 分類專案類型
            project_type = self.classify_project(remote_url, project_name)

            # 取得最後 commit 資訊
            last_commit_date = ""
            last_commit_message = ""
            try:
                result = subprocess.run(
                    ["git", "log", "-1", "--format=%ci|||%s"],
                    cwd=project_dir,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    parts = result.stdout.strip().split("|||")
                    if len(parts) == 2:
                        last_commit_date = parts[0]
                        last_commit_message = parts[1]
            except:
                pass

            # 檢測技術棧
            tech_stack = self.detect_tech_stack(project_dir)

            # 讀取 README 第一行作為摘要
            summary = self.extract_readme_summary(project_dir)

            # 檢查是否有 AI agent 團隊
            has_claude_team = (project_dir / "CLAUDE.md").exists() or \
                             (project_dir / ".claude" / "agents").exists()

            # 檢查是否有未 commit 變更
            is_dirty = self.check_git_dirty(project_dir)

            project_info = {
                "name": project_name,
                "path": str(project_dir.relative_to(HOME)),
                "type": project_type,
                "remote_url": remote_url,
                "tech_stack": tech_stack,
                "summary": summary,
                "has_claude_team": has_claude_team,
                "last_commit_date": last_commit_date,
                "last_commit_message": last_commit_message,
                "is_dirty": is_dirty
            }

            self.data["categories"]["dev_projects"]["items"].append(project_info)

        self.data["categories"]["dev_projects"]["count"] = len(
            self.data["categories"]["dev_projects"]["items"]
        )

    def classify_project(self, remote_url: str, project_name: str) -> str:
        """分類專案類型"""
        if not remote_url:
            return "own-dev"  # 自有開發（無 remote）

        # 公司專案判斷
        company_keywords = ["mayohr", "apollo", "mayo"]
        if any(keyword in remote_url.lower() for keyword in company_keywords):
            return "work"  # 工作專案

        # GitHub 參考專案
        if "github.com" in remote_url:
            # 檢查是否為自己的 repo（假設用戶名為 paul 或 paulhuang）
            user_keywords = ["paul"]
            if any(keyword in remote_url.lower() for keyword in user_keywords):
                return "own-dev"
            else:
                return "github-ref"  # GitHub 參考

        return "other"  # 其他下載

    def detect_tech_stack(self, project_dir: Path) -> List[str]:
        """檢測技術棧"""
        stack = []

        # .NET / C#（遞迴搜尋，但限制深度）
        if list(project_dir.glob("*.sln")) or \
           list(project_dir.glob("**/*.sln")) or \
           list(project_dir.glob("*.csproj")) or \
           list(project_dir.glob("**/*.csproj"))[:1]:  # 至少找到一個
            stack.append(".NET/C#")

        # Node.js
        if (project_dir / "package.json").exists():
            stack.append("Node.js")

            # 檢查是否有 React
            try:
                with open(project_dir / "package.json", encoding='utf-8') as f:
                    content = f.read()
                    if "react" in content.lower():
                        stack.append("React")
                    if "next" in content.lower():
                        stack.append("Next.js")
                    if "vue" in content.lower():
                        stack.append("Vue")
            except:
                pass

        # Python
        if (project_dir / "requirements.txt").exists() or \
           (project_dir / "pyproject.toml").exists() or \
           (project_dir / "setup.py").exists():
            stack.append("Python")

        # Go
        if (project_dir / "go.mod").exists():
            stack.append("Go")

        # Rust
        if (project_dir / "Cargo.toml").exists():
            stack.append("Rust")

        # 資料庫 scripts
        if (project_dir / "migrations").exists() or \
           list(project_dir.glob("*.sql")):
            stack.append("SQL")

        return stack

    def extract_readme_summary(self, project_dir: Path) -> str:
        """提取 README 第一行作為摘要"""
        readme_files = ["README.md", "README.txt", "README"]

        for readme_name in readme_files:
            readme_path = project_dir / readme_name
            if readme_path.exists():
                try:
                    with open(readme_path, encoding='utf-8') as f:
                        lines = f.readlines()
                        # 跳過 # 標題，找第一行有內容的
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                return line[:200]  # 限制長度
                            # 或者如果是 # 標題，移除 # 號
                            if line.startswith('#'):
                                return line.lstrip('#').strip()[:200]
                except:
                    pass

        return ""

    # Helper methods
    def extract_frontmatter(self, content: str) -> Dict[str, str]:
        """提取 YAML frontmatter"""
        match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return {}

        frontmatter = {}
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        return frontmatter

    def extract_applicability(self, content: str) -> List[str]:
        """提取 applicability"""
        match = re.search(r'## Applicability\s*\n\s*- Applies to:\s*(.+)', content)
        if not match:
            return []

        return [x.strip() for x in match.group(1).split(',')]

    def is_global_skill(self, skill_name: str) -> bool:
        """檢查是否為全域 skill"""
        return any(
            s["name"] == skill_name
            for s in self.data["categories"]["global_skills"]["items"]
        )

    def check_git_dirty(self, repo_path: Path) -> bool:
        """檢查 Git 是否有未 commit 變更"""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            return bool(result.stdout.strip())
        except:
            return False

    def run_scan(self):
        """執行完整掃描"""
        print("🔍 開始掃描...")

        print("  → 掃描全域 Skills...")
        self.scan_global_skills()

        print("  → 掃描專案 Skills...")
        self.scan_project_skills()

        print("  → 掃描開發中 Skills...")
        self.scan_dev_skills()

        print("  → 掃描開發專案...")
        self.scan_dev_projects()

        print("  → 掃描全域 Rules...")
        self.scan_global_rules()

        print("  → 掃描專案 Rules...")
        self.scan_project_rules()

        print("  → 掃描 Agents...")
        self.scan_agents()

        print("  → 掃描 Commands...")
        self.scan_commands()

        print("✓ 掃描完成！")

        return self.data

    def save_to_file(self, output_path: str):
        """儲存到 JSON 檔案"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

        print(f"💾 資料已儲存到: {output_path}")

    def print_summary(self):
        """印出摘要"""
        print("\n" + "="*60)
        print("📊 掃描摘要")
        print("="*60)
        print(f"全域 Skills:     {self.data['categories']['global_skills']['count']}")
        print(f"專案 Skills:     {self.data['categories']['project_skills']['count']}")
        print(f"開發中 Skills:   {self.data['categories']['dev_skills']['count']}")
        print(f"開發專案:        {self.data['categories']['dev_projects']['count']}")
        print(f"全域 Rules:      {self.data['categories']['global_rules']['count']}")
        print(f"專案 Rules:      {self.data['categories']['project_rules']['count']}")
        print(f"Agents:          {self.data['categories']['agents']['count']}")
        print(f"Commands:        {self.data['categories']['commands']['count']}")
        print("="*60)

        # Dev Projects 分類統計
        if self.data['categories']['dev_projects']['count'] > 0:
            projects = self.data['categories']['dev_projects']['items']
            work_count = sum(1 for p in projects if p['type'] == 'work')
            own_count = sum(1 for p in projects if p['type'] == 'own-dev')
            github_count = sum(1 for p in projects if p['type'] == 'github-ref')
            other_count = sum(1 for p in projects if p['type'] == 'other')

            print("\n📁 專案分類:")
            print(f"  工作專案:      {work_count}")
            print(f"  自有開發:      {own_count}")
            print(f"  GitHub 參考:   {github_count}")
            print(f"  其他下載:      {other_count}")

        print("\n📍 分層統計:")
        print(f"  Entry Layer:")
        print(f"    - Skills:    {len(self.data['layers']['entry']['skills'])}")
        print(f"    - Commands:  {len(self.data['layers']['entry']['commands'])}")
        print(f"  Coordination Layer:")
        print(f"    - Coordinators: {len(self.data['layers']['coordination']['coordinators'])}")
        print(f"  Execution Layer:")
        print(f"    - Workers:   {len(self.data['layers']['execution']['workers'])}")

if __name__ == "__main__":
    scanner = RealDataScanner()
    data = scanner.run_scan()

    # 儲存資料
    output_file = Path(__file__).parent / "control-center-real-data.json"
    scanner.save_to_file(str(output_file))

    # 印出摘要
    scanner.print_summary()

    print(f"\n✨ 下一步: 使用此資料生成視覺化 HTML")
