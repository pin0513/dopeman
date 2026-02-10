#!/usr/bin/env python3
"""
Scan directories to identify and register team structures.
"""

import os
import json
from pathlib import Path
from datetime import datetime


def is_team_structure(path):
    """
    Check if a directory is a valid team structure.

    Criteria (New format):
    - Has CLAUDE.md at root
    - Has .claude/agents/ directory

    Or (Legacy format):
    - Has SKILL.md at root
    - Has agents/ directory (without .claude/)
    """
    path = Path(path)

    # New format
    if (path / "CLAUDE.md").exists() and (path / ".claude" / "agents").exists():
        return True

    # Legacy format
    if (path / "SKILL.md").exists() and (path / "agents").exists():
        return True

    return False


def count_team_resources(team_path):
    """Count agents, skills, and rules in a team."""
    team_path = Path(team_path)

    agents_count = 0
    skills_count = 0
    rules_count = 0

    # Check for new format (.claude/) or legacy format
    if (team_path / ".claude").exists():
        # New format
        agents_dir = team_path / ".claude" / "agents"
        skills_dir = team_path / ".claude" / "skills"
        rules_dir = team_path / ".claude" / "rules"
    else:
        # Legacy format
        agents_dir = team_path / "agents"
        skills_dir = team_path / "skills"
        rules_dir = team_path / "rules"

    # Count agents (all .md files in agents/ and subdirectories)
    if agents_dir.exists():
        agents_count = len(list(agents_dir.rglob("*.md")))

    # Count skills (all SKILL.md files)
    if skills_dir.exists():
        skills_count = len(list(skills_dir.rglob("SKILL.md")))

    # Count rules (all .md files in rules/)
    if rules_dir.exists():
        rules_count = len([f for f in rules_dir.glob("*.md")])

    return agents_count, skills_count, rules_count


def extract_team_description(team_path):
    """Extract description from CLAUDE.md or SKILL.md."""
    team_path = Path(team_path)

    # Try CLAUDE.md first (new format)
    claude_md = team_path / "CLAUDE.md"
    if not claude_md.exists():
        # Try SKILL.md (legacy format)
        claude_md = team_path / "SKILL.md"

    if not claude_md.exists():
        return "No description available"

    try:
        with open(claude_md, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Look for first paragraph after title
        for i, line in enumerate(lines):
            if line.strip().startswith('# '):
                # Found title, get next non-empty line
                for j in range(i+1, len(lines)):
                    desc = lines[j].strip()
                    if desc and not desc.startswith('#'):
                        return desc[:200]  # Limit to 200 chars

        return "No description found"
    except Exception as e:
        return f"Error reading description: {e}"


def check_github_repo(team_path):
    """Check if team has a GitHub remote."""
    team_path = Path(team_path)
    git_config = team_path / ".git" / "config"

    if not git_config.exists():
        return None

    try:
        with open(git_config, 'r') as f:
            content = f.read()

        # Simple regex to find github URL
        import re
        match = re.search(r'url = (https://github\.com/[^\s]+)', content)
        if match:
            return match.group(1).replace('.git', '')

        return None
    except Exception:
        return None


def scan_directory(base_path):
    """
    Scan a directory for team structures.

    Returns a list of team info dicts.
    """
    base_path = Path(base_path).expanduser()

    if not base_path.exists():
        print(f"❌ Directory not found: {base_path}")
        return []

    teams = []

    print(f"🔍 Scanning {base_path} for teams...")

    # Scan immediate subdirectories
    for item in base_path.iterdir():
        if not item.is_dir():
            continue

        if item.name.startswith('.'):
            continue

        if is_team_structure(item):
            print(f"  ✓ Found team: {item.name}")

            agents_count, skills_count, rules_count = count_team_resources(item)
            description = extract_team_description(item)
            github_repo = check_github_repo(item)

            # Get creation date from git or file mtime
            created_at = None
            git_dir = item / ".git"
            if git_dir.exists():
                # Try to get first commit date
                import subprocess
                try:
                    result = subprocess.run(
                        ["git", "log", "--reverse", "--format=%ci", "--max-count=1"],
                        cwd=item,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        created_at = result.stdout.strip()[:10]  # YYYY-MM-DD
                except Exception:
                    pass

            if not created_at:
                # Fallback to CLAUDE.md modification time
                claude_md = item / "CLAUDE.md"
                if claude_md.exists():
                    mtime = claude_md.stat().st_mtime
                    created_at = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

            team_info = {
                "name": item.name,
                "path": str(item.absolute()),
                "source": "a-team",  # Assume a-team for now
                "created_at": created_at or datetime.now().strftime("%Y-%m-%d"),
                "description": description,
                "type": "team",
                "deployment_modes": ["subagent", "agent-teams"],  # Default both
                "github_repo": github_repo,
                "agents_count": agents_count,
                "skills_count": skills_count,
                "rules_count": rules_count
            }

            teams.append(team_info)

    return teams


def update_teams_registry(teams, registry_path=None):
    """Update teams-registry.json with scanned teams."""
    if registry_path is None:
        registry_path = Path.home() / ".claude" / "memory" / "dopeman" / "teams-registry.json"
    else:
        registry_path = Path(registry_path)

    # Ensure directory exists
    registry_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing registry or create new
    if registry_path.exists():
        with open(registry_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "teams": []
        }

    # Merge new teams with existing (by name)
    existing_names = {team['name']: team for team in data['teams']}

    for team in teams:
        existing_names[team['name']] = team

    # Update registry
    data['teams'] = list(existing_names.values())
    data['last_updated'] = datetime.now().isoformat()

    # Write back
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Updated teams-registry.json")
    print(f"   Location: {registry_path}")
    print(f"   Total teams: {len(data['teams'])}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Scan directories for team structures')
    parser.add_argument('paths', nargs='*',
                       default=[os.path.expanduser('~/AgentProjects/TeamProjects')],
                       help='Directories to scan (default: ~/AgentProjects/TeamProjects)')
    parser.add_argument('--registry',
                       help='Path to teams-registry.json (default: ~/.claude/memory/dopeman/teams-registry.json)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without updating registry')

    args = parser.parse_args()

    all_teams = []

    for path in args.paths:
        teams = scan_directory(path)
        all_teams.extend(teams)

    if not all_teams:
        print("\n❌ No teams found")
        return

    print(f"\n📊 Scan Summary:")
    print(f"   Found {len(all_teams)} teams")
    print()

    for team in all_teams:
        print(f"   📦 {team['name']}")
        print(f"      Path: {team['path']}")
        print(f"      Agents: {team['agents_count']}, Skills: {team['skills_count']}, Rules: {team['rules_count']}")
        if team['github_repo']:
            print(f"      GitHub: {team['github_repo']}")
        print()

    if args.dry_run:
        print("🔍 Dry run mode - no changes made")
    else:
        update_teams_registry(all_teams, args.registry)


if __name__ == '__main__':
    main()
