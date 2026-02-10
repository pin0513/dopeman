#!/bin/bash
#
# DopeMAN - Official Skills/Teams Installer Wrapper
# 快速啟動官方 Skills/Teams 安裝管理器
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/install-official.py"

# 檢查 Python 腳本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ 找不到安裝腳本: $PYTHON_SCRIPT"
    exit 1
fi

# 賦予執行權限
chmod +x "$PYTHON_SCRIPT"

# 執行 Python 腳本
python3 "$PYTHON_SCRIPT" "$@"
