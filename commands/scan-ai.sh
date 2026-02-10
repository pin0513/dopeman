#!/bin/bash
#
# DopeMAN - AI Platform Scanner (統一入口)
# 掃描多個 AI 平台的配置並合併結果
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_DIR="$HOME/.claude/memory/dopeman"
COMBINED_RESULT="$MEMORY_DIR/ai-platforms-scan.json"

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 預設值
PLATFORM=""
VERBOSE=""
ALL_PLATFORMS=false

# 解析參數
while [[ $# -gt 0 ]]; do
    case $1 in
        --platform=*)
            PLATFORM="${1#*=}"
            shift
            ;;
        --all)
            ALL_PLATFORMS=true
            shift
            ;;
        --verbose|-v)
            VERBOSE="--verbose"
            shift
            ;;
        --help|-h)
            cat << EOF
DopeMAN - AI Platform Scanner

使用方式:
  $0 --platform=<platform> [options]
  $0 --all [options]

參數:
  --platform=<platform>   指定平台 (gemini, openai)
  --all                   掃描所有支援的平台
  --verbose, -v           詳細輸出
  --help, -h              顯示此說明

範例:
  $0 --platform=gemini
  $0 --platform=openai --verbose
  $0 --all

EOF
            exit 0
            ;;
        *)
            echo -e "${RED}未知參數: $1${NC}"
            echo "使用 --help 查看說明"
            exit 1
            ;;
    esac
done

# 檢查參數
if [[ -z "$PLATFORM" && "$ALL_PLATFORMS" = false ]]; then
    echo -e "${RED}錯誤: 請指定 --platform 或 --all${NC}"
    echo "使用 --help 查看說明"
    exit 1
fi

# 確保 memory 目錄存在
mkdir -p "$MEMORY_DIR"

# 初始化合併結果
cat > "$COMBINED_RESULT" << EOF
{
  "version": "1.0.0",
  "scan_time": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "platforms": {},
  "summary": {
    "total_platforms": 0,
    "platforms_found": 0,
    "platforms_not_found": 0,
    "total_tools": 0,
    "total_mappings": 0
  }
}
EOF

# 掃描函數
scan_platform() {
    local platform=$1
    local scanner_script=""
    local result_file=""

    case $platform in
        gemini)
            scanner_script="$SCRIPT_DIR/scan-gemini.py"
            result_file="$MEMORY_DIR/gemini-scan.json"
            ;;
        openai)
            scanner_script="$SCRIPT_DIR/scan-openai.py"
            result_file="$MEMORY_DIR/openai-scan.json"
            ;;
        *)
            echo -e "${RED}不支援的平台: $platform${NC}"
            return 1
            ;;
    esac

    # 檢查 scanner 是否存在
    if [[ ! -f "$scanner_script" ]]; then
        echo -e "${RED}找不到掃描器: $scanner_script${NC}"
        return 1
    fi

    # 執行掃描
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}掃描平台: $platform${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    if python3 "$scanner_script" $VERBOSE; then
        echo ""
        echo -e "${GREEN}✅ $platform 掃描成功${NC}"

        # 合併結果（如果結果檔案存在）
        if [[ -f "$result_file" ]]; then
            merge_result "$platform" "$result_file"
        fi
    else
        exit_code=$?
        echo ""
        echo -e "${YELLOW}⚠️  $platform 掃描完成（有警告或錯誤）${NC}"

        # 即使有錯誤也嘗試合併結果
        if [[ -f "$result_file" ]]; then
            merge_result "$platform" "$result_file"
        fi

        # 如果是 "not installed" 錯誤（exit code 1），不算致命錯誤
        if [[ $exit_code -eq 1 ]]; then
            return 0
        fi

        return $exit_code
    fi

    echo ""
}

# 合併結果函數
merge_result() {
    local platform=$1
    local result_file=$2

    if [[ ! -f "$result_file" ]]; then
        return
    fi

    # 使用 Python 合併 JSON
    python3 << EOF
import json

# 讀取合併結果
with open("$COMBINED_RESULT", 'r', encoding='utf-8') as f:
    combined = json.load(f)

# 讀取平台結果
with open("$result_file", 'r', encoding='utf-8') as f:
    platform_data = json.load(f)

# 合併
combined["platforms"]["$platform"] = platform_data

# 更新摘要
combined["summary"]["total_platforms"] += 1

if platform_data.get("config_exists"):
    combined["summary"]["platforms_found"] += 1
else:
    combined["summary"]["platforms_not_found"] += 1

# 計算總工具數
if "$platform" == "gemini":
    combined["summary"]["total_tools"] += platform_data.get("tools", {}).get("count", 0)
elif "$platform" == "openai":
    combined["summary"]["total_tools"] += platform_data.get("functions", {}).get("count", 0)
    combined["summary"]["total_tools"] += platform_data.get("assistants", {}).get("count", 0)

# 計算總映射數
combined["summary"]["total_mappings"] += len(platform_data.get("mappings", {}).get("to_claude_skills", []))

# 儲存
with open("$COMBINED_RESULT", 'w', encoding='utf-8') as f:
    json.dump(combined, f, indent=2, ensure_ascii=False)
EOF
}

# 列印摘要
print_summary() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}📊 掃描摘要${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    python3 << EOF
import json

with open("$COMBINED_RESULT", 'r', encoding='utf-8') as f:
    data = json.load(f)

summary = data["summary"]

print(f"   掃描平台: {summary['total_platforms']} 個")
print(f"   已安裝: {summary['platforms_found']} 個")
print(f"   未安裝: {summary['platforms_not_found']} 個")
print(f"   總工具數: {summary['total_tools']} 個")
print(f"   總映射數: {summary['total_mappings']} 個")
print()
print("已掃描的平台:")
for platform in data["platforms"]:
    status = "✅" if data["platforms"][platform]["config_exists"] else "❌"
    print(f"   {status} {platform}")

print()
print(f"💾 合併結果已儲存: $COMBINED_RESULT")
EOF

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# 主流程
main() {
    if [[ "$ALL_PLATFORMS" = true ]]; then
        # 掃描所有支援的平台
        for platform in gemini openai; do
            scan_platform "$platform" || true
        done
    else
        # 掃描指定平台
        scan_platform "$PLATFORM"
    fi

    # 列印摘要
    if [[ "$ALL_PLATFORMS" = true ]] || [[ $(python3 -c "import json; print(len(json.load(open('$COMBINED_RESULT'))['platforms']))") -gt 1 ]]; then
        print_summary
    fi
}

main
