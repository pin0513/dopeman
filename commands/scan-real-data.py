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
MEMORY_DIR = CLAUDE_DIR / "memory" / "dopeman"

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
            },
            "user_preferences": {}
        }
        # 載入用戶設定
        self.load_user_preferences()

    def load_user_preferences(self):
        """載入用戶設定檔"""
        pref_file = MEMORY_DIR / "user-preferences.json"

        # 如果設定檔不存在，建立預設設定
        if not pref_file.exists():
            default_prefs = {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "preferences": {
                    "default_editor": "vscode",
                    "editor_tools": [
                        {
                            "id": "vscode",
                            "name": "Visual Studio Code",
                            "protocol": "vscode://file",
                            "enabled": True,
                            "icon": "📂"
                        },
                        {
                            "id": "cursor",
                            "name": "Cursor",
                            "protocol": "cursor://file",
                            "enabled": True,
                            "icon": "🔮"
                        },
                        {
                            "id": "warp",
                            "name": "Warp Terminal",
                            "protocol": "warp://file",
                            "enabled": True,
                            "icon": "⚡"
                        }
                    ],
                    "dashboard": {
                        "theme": "light",
                        "auto_refresh": False,
                        "refresh_interval": 300
                    }
                }
            }
            # 確保目錄存在
            MEMORY_DIR.mkdir(parents=True, exist_ok=True)
            pref_file.write_text(json.dumps(default_prefs, indent=2, ensure_ascii=False), encoding='utf-8')
            self.data["user_preferences"] = default_prefs["preferences"]
        else:
            # 讀取現有設定
            try:
                prefs = json.loads(pref_file.read_text(encoding='utf-8'))
                self.data["user_preferences"] = prefs.get("preferences", {})
            except Exception as e:
                print(f"⚠️  無法讀取用戶設定: {e}")
                self.data["user_preferences"] = {}

    def scan_global_skills(self):
        """掃描全域 Skills（支援 symlinks）"""
        skills_dir = CLAUDE_DIR / "skills"
        if not skills_dir.exists():
            return

        # 遍歷 skills 目錄下的所有項目（包含 symlinks）
        for item in skills_dir.iterdir():
            # 跳過非目錄且非 symlink 的項目
            if not item.is_dir() and not item.is_symlink():
                continue

            # 如果是 symlink，解析到實際路徑
            real_path = item.resolve() if item.is_symlink() else item

            # 檢查是否有 SKILL.md
            skill_md_path = real_path / "SKILL.md"
            if not skill_md_path.exists():
                continue

            # 排除 node_modules
            if "node_modules" in str(real_path):
                continue

            skill_name = real_path.name

            # 讀取 YAML frontmatter
            content = skill_md_path.read_text(encoding='utf-8')
            frontmatter = self.extract_frontmatter(content)

            # 判斷是否為 team skill (有 .claude/agents/)
            has_agents = (real_path / ".claude" / "agents").exists()

            skill_info = {
                "name": skill_name,
                "path": str(real_path.relative_to(HOME)),
                "type": "team" if has_agents else "single",
                "description": frontmatter.get("description", ""),
                "source": "local",
                "has_agents": has_agents,
                "has_git": (real_path / ".git").exists()
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

            # 檢查是否有 SKILL.md（只有 SKILL.md 才算是開發中的 skill）
            # .claude/ 目錄只是 Claude Code 專案設定，不代表是 skill
            has_skill = (project_dir / "SKILL.md").exists()

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
        """掃描 Agents（遞迴掃描所有層級）"""
        # 遞迴掃描所有 .claude/agents 目錄
        for claude_dir in DEV_DIR.rglob(".claude"):
            if "node_modules" in str(claude_dir) or str(claude_dir) == str(CLAUDE_DIR):
                continue

            project_path = claude_dir.parent
            agents_dir = claude_dir / "agents"

            if not agents_dir.exists():
                continue

            # 遞迴掃描所有 .md 檔案（支援多層巢狀）
            for agent_path in agents_dir.rglob("*.md"):
                # 計算相對於 agents_dir 的深度
                relative_path = agent_path.relative_to(agents_dir)
                depth = len(relative_path.parts) - 1  # 減去檔案本身

                # 根據深度和位置判斷類型
                if depth == 0:
                    # agents/ 根目錄 → coordinator
                    agent_type = "coordinator"
                    group = None
                    layer = "coordination"
                else:
                    # 子目錄 → worker
                    agent_type = "worker"
                    # 支援多層巢狀，使用完整路徑作為群組名稱
                    group = str(relative_path.parent).replace('/', ' > ')
                    layer = "execution"

                agent_info = {
                    "name": agent_path.stem,
                    "path": str(agent_path.relative_to(HOME)),
                    "type": agent_type,
                    "group": group,
                    "depth": depth,
                    "belongs_to_project": str(project_path.relative_to(HOME)),
                }

                self.data["categories"]["agents"]["items"].append(agent_info)

                # 加入對應的層級
                if layer == "coordination":
                    if agent_path.stem not in self.data["layers"]["coordination"]["coordinators"]:
                        self.data["layers"]["coordination"]["coordinators"].append(agent_path.stem)
                else:
                    if agent_path.stem not in self.data["layers"]["execution"]["workers"]:
                        self.data["layers"]["execution"]["workers"].append(agent_path.stem)

        self.data["categories"]["agents"]["count"] = len(
            self.data["categories"]["agents"]["items"]
        )

    def scan_commands(self):
        """掃描 Commands（從 SKILL.md 動態提取）"""
        # 遞迴掃描所有 SKILL.md
        for skill_path in CLAUDE_DIR.rglob("SKILL.md"):
            if "node_modules" in str(skill_path):
                continue

            skill_name = skill_path.parent.name
            content = skill_path.read_text(encoding='utf-8')

            # 提取 description（從 YAML frontmatter 或第一個標題）
            description = self._extract_skill_description(content, skill_name)

            # 1. 先加入 skill 本身作為基礎命令
            base_cmd = {
                "name": skill_name,
                "full_command": f"/{skill_name}",
                "entry_skill": skill_name,
                "description": description,
                "aliases": [],
                "is_base_command": True
            }
            self.data["categories"]["commands"]["items"].append(base_cmd)
            self.data["layers"]["entry"]["commands"].append(base_cmd["full_command"])

            # 2. 檢查是否有子命令表格（如 dopeman 的多個子命令）
            lines = content.split('\n')
            in_command_table = False

            for i, line in enumerate(lines):
                # 檢查是否進入命令表格區域
                if '可用命令' in line or ('命令' in line and '說明' in line):
                    # 找到表格開始（下一行或下兩行應該是表格）
                    for j in range(i, min(i+5, len(lines))):
                        if '|' in lines[j] and ('---' in lines[j+1] if j+1 < len(lines) else False):
                            in_command_table = True
                            table_start = j + 2  # 跳過標題和分隔線
                            break

                    if in_command_table:
                        # 解析表格內容
                        for k in range(table_start, len(lines)):
                            line = lines[k].strip()

                            # 表格結束
                            if not line or not line.startswith('|'):
                                break

                            # 解析表格行
                            parts = [p.strip() for p in line.split('|')]
                            if len(parts) >= 4:  # | 命令 | 說明 | 範例 |
                                # 清理命令名稱：移除所有 backticks 和參數
                                cmd_text = parts[1].replace('`', '').strip()

                                # 檢查是否有別名（在移除 backticks 之前）
                                alias_match = re.search(r'\(別名:\s*`?(.+?)`?\)', parts[1])
                                aliases = [a.strip() for a in alias_match.group(1).split(',')] if alias_match else []

                                # 移除別名部分，只保留命令名稱
                                cmd_name = re.sub(r'\s*\(別名:.*?\)', '', cmd_text).split()[0]
                                cmd_desc = parts[2]

                                cmd_info = {
                                    "name": cmd_name,
                                    "full_command": f"/{skill_name} {cmd_name}",
                                    "entry_skill": skill_name,
                                    "description": cmd_desc,
                                    "aliases": aliases,
                                    "is_subcommand": True
                                }

                                self.data["categories"]["commands"]["items"].append(cmd_info)
                                self.data["layers"]["entry"]["commands"].append(cmd_info["full_command"])

                                # 也加入別名
                                for alias in aliases:
                                    self.data["layers"]["entry"]["commands"].append(f"/{skill_name} {alias}")

                        break  # 找到並處理完表格後跳出

        self.data["categories"]["commands"]["count"] = len(
            self.data["categories"]["commands"]["items"]
        )

    def _extract_skill_description(self, content: str, skill_name: str) -> str:
        """從 SKILL.md 提取簡短描述"""
        lines = content.split('\n')

        # 嘗試從 YAML frontmatter 提取 description
        if lines[0].strip() == '---':
            in_frontmatter = True
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    break
                if line.startswith('description:'):
                    # 可能是多行 description
                    desc_lines = [line.split('description:', 1)[1].strip()]
                    # 檢查後續行是否為縮排的延續
                    for j in range(i+1, len(lines)):
                        if lines[j].startswith('  ') or lines[j].startswith('\t'):
                            desc_lines.append(lines[j].strip())
                        elif lines[j].strip() == '---':
                            break
                        else:
                            break
                    description = ' '.join(desc_lines).replace('|', '').strip()
                    # 只取第一句話
                    if '。' in description:
                        description = description.split('。')[0] + '。'
                    elif '.' in description and len(description) > 100:
                        description = description.split('.')[0] + '.'
                    return description[:150]  # 最多 150 字元

        # 如果沒有 frontmatter，嘗試從第一個段落提取
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('---'):
                if '。' in line:
                    return line.split('。')[0] + '。'
                return line[:100]

        return f"執行 {skill_name}"

    def scan_dev_projects(self):
        """掃描開發專案"""
        import subprocess

        # 掃描 ~/DEV 下所有有 .git 的專案（遞迴搜尋）
        # 過濾掉不需要的子專案（node_modules, .venv, vendor 等）
        exclude_patterns = ["node_modules", ".venv", "venv", "vendor", ".git/modules"]

        all_git_dirs = []
        for git_dir in DEV_DIR.rglob(".git"):
            # 跳過非目錄的 .git 檔案
            if not git_dir.is_dir():
                continue

            # 檢查路徑是否包含排除的模式
            path_str = str(git_dir.relative_to(DEV_DIR))
            if any(exclude in path_str for exclude in exclude_patterns):
                continue

            all_git_dirs.append(git_dir)

        # 過濾掉巢狀的 git 專案（只保留最上層）
        top_level_git_dirs = []
        for git_dir in sorted(all_git_dirs):
            project_dir = git_dir.parent

            # 檢查是否為其他已加入專案的子專案
            is_nested = False
            for other_git_dir in all_git_dirs:
                if git_dir == other_git_dir:
                    continue
                other_project_dir = other_git_dir.parent
                # 如果此專案在另一個專案目錄內，則為巢狀專案
                if project_dir != other_project_dir and str(project_dir).startswith(str(other_project_dir) + "/"):
                    is_nested = True
                    break

            if not is_nested:
                top_level_git_dirs.append(git_dir)

        # 掃描所有最上層 git 專案
        for git_dir in top_level_git_dirs:
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
