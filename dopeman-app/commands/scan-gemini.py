#!/usr/bin/env python3
"""
DopeMAN - Gemini Platform Scanner
掃描 Gemini AI 環境配置，轉換為統一 JSON 格式
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 路徑配置
HOME = Path.home()
GEMINI_DIR = HOME / ".gemini"
MEMORY_DIR = HOME / ".claude" / "memory" / "dopeman"


class GeminiScanner:
    def __init__(self):
        self.scan_result = {
            "platform": "gemini",
            "version": "1.0.0",
            "scan_time": datetime.now().isoformat(),
            "config_exists": False,
            "config_path": str(GEMINI_DIR),
            "config": {},
            "tools": {"count": 0, "items": []},
            "prompts": {"count": 0, "items": []},
            "mappings": {
                "to_claude_skills": [],
                "suggestions": []
            },
            "errors": []
        }

    def check_gemini_installation(self) -> bool:
        """檢查 Gemini 是否安裝"""
        if not GEMINI_DIR.exists():
            self.scan_result["errors"].append({
                "type": "not_installed",
                "message": f"Gemini 配置目錄不存在: {GEMINI_DIR}"
            })
            return False

        self.scan_result["config_exists"] = True
        return True

    def load_config(self):
        """載入 Gemini 配置"""
        config_file = GEMINI_DIR / "config.json"

        if not config_file.exists():
            self.scan_result["errors"].append({
                "type": "no_config",
                "message": "找不到 config.json"
            })
            return

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.scan_result["config"] = json.load(f)
        except Exception as e:
            self.scan_result["errors"].append({
                "type": "config_error",
                "message": f"無法讀取配置檔: {e}"
            })

    def scan_tools(self):
        """掃描 Gemini Tools（等同 Claude Skills）"""
        tools_dir = GEMINI_DIR / "tools"

        if not tools_dir.exists():
            self.scan_result["errors"].append({
                "type": "no_tools",
                "message": "找不到 tools/ 目錄"
            })
            return

        for tool_file in tools_dir.iterdir():
            if tool_file.suffix not in [".json", ".yaml", ".yml"]:
                continue

            try:
                tool_data = self._load_json_or_yaml(tool_file)

                tool_info = {
                    "name": tool_file.stem,
                    "path": str(tool_file),
                    "type": tool_file.suffix[1:],
                    "description": tool_data.get("description", ""),
                    "parameters": tool_data.get("parameters", {}),
                    "metadata": tool_data.get("metadata", {})
                }

                self.scan_result["tools"]["items"].append(tool_info)
                self.scan_result["tools"]["count"] += 1

                # 嘗試映射到 Claude Skills
                self._map_to_claude_skill(tool_info)

            except Exception as e:
                self.scan_result["errors"].append({
                    "type": "tool_error",
                    "path": str(tool_file),
                    "message": f"無法讀取工具: {e}"
                })

    def scan_prompts(self):
        """掃描 Gemini Prompts"""
        prompts_dir = GEMINI_DIR / "prompts"

        if not prompts_dir.exists():
            self.scan_result["errors"].append({
                "type": "no_prompts",
                "message": "找不到 prompts/ 目錄"
            })
            return

        for prompt_file in prompts_dir.iterdir():
            if prompt_file.suffix not in [".txt", ".md", ".json"]:
                continue

            try:
                if prompt_file.suffix == ".json":
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        prompt_data = json.load(f)
                    content = prompt_data.get("content", "")
                    metadata = prompt_data
                else:
                    content = prompt_file.read_text(encoding='utf-8')
                    metadata = {}

                prompt_info = {
                    "name": prompt_file.stem,
                    "path": str(prompt_file),
                    "type": prompt_file.suffix[1:],
                    "content_preview": content[:200] + "..." if len(content) > 200 else content,
                    "metadata": metadata
                }

                self.scan_result["prompts"]["items"].append(prompt_info)
                self.scan_result["prompts"]["count"] += 1

            except Exception as e:
                self.scan_result["errors"].append({
                    "type": "prompt_error",
                    "path": str(prompt_file),
                    "message": f"無法讀取 prompt: {e}"
                })

    def _load_json_or_yaml(self, file_path: Path) -> Dict:
        """載入 JSON 或 YAML 檔案"""
        if file_path.suffix == ".json":
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # YAML
            try:
                import yaml
                with open(file_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except ImportError:
                raise Exception("需要安裝 PyYAML: pip install pyyaml")

    def _map_to_claude_skill(self, tool_info: Dict):
        """嘗試映射 Gemini Tool 到 Claude Skill"""
        tool_name = tool_info["name"].lower()
        description = tool_info.get("description", "").lower()

        # 映射規則
        mappings = {
            "code": ["dev-team-pm", "dev-team-architect"],
            "assistant": ["dev-team-pm"],
            "doc": ["article-writer", "article-editor"],
            "generator": ["article-writer"],
            "test": ["dev-team-qa"],
            "runner": ["dev-team-qa"],
            "slide": ["slide-maker", "slide-consult"],
            "presentation": ["slide-maker"]
        }

        matched_skills = []
        for keyword, skills in mappings.items():
            if keyword in tool_name or keyword in description:
                matched_skills.extend(skills)

        if matched_skills:
            self.scan_result["mappings"]["to_claude_skills"].append({
                "gemini_tool": tool_info["name"],
                "claude_skills": list(set(matched_skills)),
                "confidence": "high" if len(matched_skills) == 1 else "medium"
            })

            self.scan_result["mappings"]["suggestions"].append({
                "message": f"💡 {tool_info['name']} 可對應到 Claude skill: {', '.join(set(matched_skills))}"
            })

    def save_result(self):
        """儲存掃描結果"""
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        result_file = MEMORY_DIR / "gemini-scan.json"

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(self.scan_result, f, indent=2, ensure_ascii=False)

        return result_file

    def print_result(self, verbose: bool = False):
        """列印掃描結果"""
        print("🔍 DopeMAN - AI 平台掃描 (Gemini)")
        print("━" * 50)
        print()

        if not self.scan_result["config_exists"]:
            print(f"❌ Gemini 未安裝或配置不存在")
            print(f"   路徑: {self.scan_result['config_path']}")
            print()
            print("💡 如果您使用 Gemini，請確保配置目錄存在：")
            print(f"   mkdir -p {self.scan_result['config_path']}")
            return

        print("📂 掃描 Gemini 配置目錄...")
        print(f"   路徑: {self.scan_result['config_path']}")
        print()

        # 配置檔案
        if self.scan_result["config"]:
            print("⚙️  發現配置檔案:")
            print("   ✅ config.json")
            if verbose:
                print(f"   配置內容: {json.dumps(self.scan_result['config'], indent=6, ensure_ascii=False)}")
            print()

        # Tools
        print(f"📦 Gemini Tools (等同 Claude Skills):")
        print(f"   總計: {self.scan_result['tools']['count']} 個")
        if self.scan_result['tools']['items']:
            for tool in self.scan_result['tools']['items']:
                print(f"   - {tool['name']}")
                if verbose and tool.get('description'):
                    print(f"     描述: {tool['description']}")
            print()

        # Prompts
        print(f"📝 Gemini Prompts:")
        print(f"   總計: {self.scan_result['prompts']['count']} 個")
        if self.scan_result['prompts']['items'] and verbose:
            for prompt in self.scan_result['prompts']['items']:
                print(f"   - {prompt['name']}")
            print()

        # 轉換建議
        if self.scan_result['mappings']['suggestions']:
            print("🔄 轉換建議:")
            for suggestion in self.scan_result['mappings']['suggestions']:
                print(f"   {suggestion['message']}")
            print()

        # 錯誤
        if self.scan_result['errors']:
            print("⚠️  掃描時發現問題:")
            for error in self.scan_result['errors']:
                if error['type'] not in ['not_installed']:
                    print(f"   - {error['message']}")
            print()

        print("━" * 50)
        print("✅ 掃描完成")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='DopeMAN - Gemini Platform Scanner')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細輸出')
    parser.add_argument('--save', action='store_true', default=True, help='儲存結果到 JSON')

    args = parser.parse_args()

    scanner = GeminiScanner()

    # 檢查安裝
    if not scanner.check_gemini_installation():
        scanner.print_result(verbose=args.verbose)
        sys.exit(1)

    # 載入配置
    scanner.load_config()

    # 掃描 Tools 和 Prompts
    scanner.scan_tools()
    scanner.scan_prompts()

    # 列印結果
    scanner.print_result(verbose=args.verbose)

    # 儲存結果
    if args.save:
        result_file = scanner.save_result()
        print(f"💾 結果已儲存: {result_file}")
        print("━" * 50)

    # 回傳狀態碼
    if scanner.scan_result['errors']:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
