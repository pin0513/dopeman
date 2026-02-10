#!/usr/bin/env python3
"""
DopeMAN - OpenAI Code Platform Scanner
掃描 OpenAI Code 環境配置，轉換為統一 JSON 格式
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 路徑配置
HOME = Path.home()
OPENAI_DIR = HOME / ".openai"
MEMORY_DIR = HOME / ".claude" / "memory" / "dopeman"


class OpenAIScanner:
    def __init__(self):
        self.scan_result = {
            "platform": "openai",
            "version": "1.0.0",
            "scan_time": datetime.now().isoformat(),
            "config_exists": False,
            "config_path": str(OPENAI_DIR),
            "config": {},
            "assistants": {"count": 0, "items": []},
            "functions": {"count": 0, "items": []},
            "mappings": {
                "to_claude_skills": [],
                "suggestions": []
            },
            "errors": []
        }

    def check_openai_installation(self) -> bool:
        """檢查 OpenAI Code 是否安裝"""
        if not OPENAI_DIR.exists():
            self.scan_result["errors"].append({
                "type": "not_installed",
                "message": f"OpenAI 配置目錄不存在: {OPENAI_DIR}"
            })
            return False

        self.scan_result["config_exists"] = True
        return True

    def load_config(self):
        """載入 OpenAI 配置"""
        config_file = OPENAI_DIR / "config.json"

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

    def scan_assistants(self):
        """掃描 OpenAI Assistants（等同 Claude Agents）"""
        assistants_dir = OPENAI_DIR / "assistants"

        if not assistants_dir.exists():
            self.scan_result["errors"].append({
                "type": "no_assistants",
                "message": "找不到 assistants/ 目錄"
            })
            return

        for assistant_file in assistants_dir.iterdir():
            if assistant_file.suffix != ".json":
                continue

            try:
                with open(assistant_file, 'r', encoding='utf-8') as f:
                    assistant_data = json.load(f)

                assistant_info = {
                    "name": assistant_data.get("name", assistant_file.stem),
                    "path": str(assistant_file),
                    "description": assistant_data.get("description", ""),
                    "model": assistant_data.get("model", "unknown"),
                    "instructions": assistant_data.get("instructions", ""),
                    "tools": assistant_data.get("tools", []),
                    "metadata": assistant_data.get("metadata", {})
                }

                self.scan_result["assistants"]["items"].append(assistant_info)
                self.scan_result["assistants"]["count"] += 1

                # 嘗試映射到 Claude Agents
                self._map_to_claude_agent(assistant_info)

            except Exception as e:
                self.scan_result["errors"].append({
                    "type": "assistant_error",
                    "path": str(assistant_file),
                    "message": f"無法讀取 assistant: {e}"
                })

    def scan_functions(self):
        """掃描 OpenAI Functions（等同 Claude Skills）"""
        functions_dir = OPENAI_DIR / "functions"

        if not functions_dir.exists():
            self.scan_result["errors"].append({
                "type": "no_functions",
                "message": "找不到 functions/ 目錄"
            })
            return

        for function_file in functions_dir.iterdir():
            if function_file.suffix != ".json":
                continue

            try:
                with open(function_file, 'r', encoding='utf-8') as f:
                    function_data = json.load(f)

                function_info = {
                    "name": function_data.get("name", function_file.stem),
                    "path": str(function_file),
                    "description": function_data.get("description", ""),
                    "parameters": function_data.get("parameters", {}),
                    "metadata": function_data.get("metadata", {})
                }

                self.scan_result["functions"]["items"].append(function_info)
                self.scan_result["functions"]["count"] += 1

                # 嘗試映射到 Claude Skills
                self._map_to_claude_skill(function_info)

            except Exception as e:
                self.scan_result["errors"].append({
                    "type": "function_error",
                    "path": str(function_file),
                    "message": f"無法讀取 function: {e}"
                })

    def _map_to_claude_agent(self, assistant_info: Dict):
        """嘗試映射 OpenAI Assistant 到 Claude Agent"""
        name = assistant_info["name"].lower()
        description = assistant_info.get("description", "").lower()
        instructions = assistant_info.get("instructions", "").lower()

        # 映射規則
        mappings = {
            "coordinator": ["dopeman-coordinator", "team-coordinator"],
            "developer": ["dev-team-pm", "dev-team-architect"],
            "tester": ["dev-team-qa"],
            "writer": ["article-writer"],
            "editor": ["article-editor"],
            "designer": ["web-produce-designer"],
            "qa": ["dev-team-qa"]
        }

        matched_agents = []
        for keyword, agents in mappings.items():
            if keyword in name or keyword in description or keyword in instructions:
                matched_agents.extend(agents)

        if matched_agents:
            self.scan_result["mappings"]["to_claude_skills"].append({
                "openai_assistant": assistant_info["name"],
                "claude_agents": list(set(matched_agents)),
                "confidence": "high" if len(matched_agents) == 1 else "medium"
            })

            self.scan_result["mappings"]["suggestions"].append({
                "message": f"💡 {assistant_info['name']} 可對應到 Claude agent: {', '.join(set(matched_agents))}"
            })

    def _map_to_claude_skill(self, function_info: Dict):
        """嘗試映射 OpenAI Function 到 Claude Skill"""
        name = function_info["name"].lower()
        description = function_info.get("description", "").lower()

        # 映射規則
        mappings = {
            "code": ["dev-team-pm", "dev-team-architect"],
            "review": ["ado-code-review", "dev-team-tech-lead"],
            "test": ["dev-team-qa"],
            "deploy": ["web-produce-deploy"],
            "commit": ["mayoform-devops"],
            "slide": ["slide-maker", "slide-consult"],
            "article": ["article-writer"],
            "web": ["web-produce-pm"]
        }

        matched_skills = []
        for keyword, skills in mappings.items():
            if keyword in name or keyword in description:
                matched_skills.extend(skills)

        if matched_skills:
            self.scan_result["mappings"]["to_claude_skills"].append({
                "openai_function": function_info["name"],
                "claude_skills": list(set(matched_skills)),
                "confidence": "high" if len(matched_skills) == 1 else "medium"
            })

            self.scan_result["mappings"]["suggestions"].append({
                "message": f"💡 {function_info['name']} 可對應到 Claude skill: {', '.join(set(matched_skills))}"
            })

    def save_result(self):
        """儲存掃描結果"""
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        result_file = MEMORY_DIR / "openai-scan.json"

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(self.scan_result, f, indent=2, ensure_ascii=False)

        return result_file

    def print_result(self, verbose: bool = False):
        """列印掃描結果"""
        print("🔍 DopeMAN - AI 平台掃描 (OpenAI Code)")
        print("━" * 50)
        print()

        if not self.scan_result["config_exists"]:
            print(f"❌ OpenAI Code 未安裝或配置不存在")
            print(f"   路徑: {self.scan_result['config_path']}")
            print()
            print("💡 如果您使用 OpenAI Code，請確保配置目錄存在：")
            print(f"   mkdir -p {self.scan_result['config_path']}")
            return

        print("📂 掃描 OpenAI Code 配置目錄...")
        print(f"   路徑: {self.scan_result['config_path']}")
        print()

        # 配置檔案
        if self.scan_result["config"]:
            print("⚙️  發現配置檔案:")
            print("   ✅ config.json")
            if verbose:
                print(f"   配置內容: {json.dumps(self.scan_result['config'], indent=6, ensure_ascii=False)}")
            print()

        # Assistants
        print(f"🤖 OpenAI Assistants (等同 Claude Agents):")
        print(f"   總計: {self.scan_result['assistants']['count']} 個")
        if self.scan_result['assistants']['items']:
            for assistant in self.scan_result['assistants']['items']:
                print(f"   - {assistant['name']}")
                if verbose and assistant.get('description'):
                    print(f"     描述: {assistant['description']}")
                    print(f"     Model: {assistant['model']}")
            print()

        # Functions
        print(f"📦 OpenAI Functions (等同 Claude Skills):")
        print(f"   總計: {self.scan_result['functions']['count']} 個")
        if self.scan_result['functions']['items']:
            for function in self.scan_result['functions']['items']:
                print(f"   - {function['name']}")
                if verbose and function.get('description'):
                    print(f"     描述: {function['description']}")
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

    parser = argparse.ArgumentParser(description='DopeMAN - OpenAI Code Platform Scanner')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細輸出')
    parser.add_argument('--save', action='store_true', default=True, help='儲存結果到 JSON')

    args = parser.parse_args()

    scanner = OpenAIScanner()

    # 檢查安裝
    if not scanner.check_openai_installation():
        scanner.print_result(verbose=args.verbose)
        sys.exit(1)

    # 載入配置
    scanner.load_config()

    # 掃描 Assistants 和 Functions
    scanner.scan_assistants()
    scanner.scan_functions()

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
