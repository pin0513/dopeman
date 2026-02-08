---
name: Version Comparison
description: 比較版本號判斷是否需要更新
---

# Version Comparison

## 描述

提供語意化版本號（Semantic Versioning）的比較邏輯，判斷 local 與 upstream 版本的差異。

## 使用者

- **skill-tracker**：判斷 local skill 是否過期
- **sync-manager**：決定哪些檔案需要同步

## 核心知識

### 版本號格式

```
v{major}.{minor}.{patch}[-{prerelease}][+{buildmetadata}]

範例：
- v1.0.0
- v2.3.1
- v1.0.0-alpha
- v1.0.0-beta.1
- v1.0.0+20130313144700
```

### 比較規則

1. **Major 版本不同**：視為重大變更，強烈建議更新
2. **Minor 版本不同**：新增功能，建議更新
3. **Patch 版本不同**：Bug 修復，可選擇性更新
4. **Commit Hash 不同**：開發中版本，提示但不強制

### 版本來源

- **標準化 Skill**：從 `---\nversion: v1.2.3\n---` 取得
- **未標準化 Skill**：從最新 commit hash 判斷

## 範例

### 比較語意化版本

```bash
# 使用 semver 工具（需安裝）
# npm install -g semver

local_version="v1.2.3"
upstream_version="v1.3.0"

if semver $local_version -lt $upstream_version; then
  echo "Update available: $local_version -> $upstream_version"
fi
```

### 比較 Commit Hash

```bash
local_hash="abc123"
upstream_hash="def456"

if [ "$local_hash" != "$upstream_hash" ]; then
  echo "Upstream has new commits"
  echo "Local:    $local_hash"
  echo "Upstream: $upstream_hash"
fi
```

### 提取版本號

```bash
# 從 frontmatter 提取
version=$(grep -E '^version:' SKILL.md | head -1 | awk '{print $2}')

# 從 git tag 提取
latest_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
```

## 範例輸出

```
[skill-tracker] Checking versions...

✅ github-api-operations: v1.2.0 (up to date)
⚠️  version-comparison: v1.1.0 → v1.2.0 available (minor update)
🔴 json-registry-manager: v2.0.0 → v3.0.0 available (major update)
📝 custom-skill: abc123 → def456 (upstream changed)
```

## 相關規則

- `rules/versioning-strategy.md`：版本號命名與更新策略
- `rules/backward-compatibility.md`：判斷是否為 breaking change
