---
name: DopeMAN Orchestration
description: 協調 DopeMAN 團隊的任務派工與狀態追蹤
---

# DopeMAN Orchestration

## 描述

專屬於 dopeman-coordinator 的調度核心技能，負責解析使用者意圖、決定派工策略、追蹤任務狀態、整合各 agent 回報。

## 使用者

- **dopeman-coordinator**：唯一使用者，團隊調度中樞

## 核心知識

### 任務類型與對應 Agent

| 使用者意圖 | 主要 Agent | 輔助 Agent |
|-----------|-----------|-----------|
| 檢查 skill 更新 | skill-tracker | - |
| 探索新 skills | skill-scout | skill-tracker |
| 整理檔案結構 | file-organizer | - |
| 同步 upstream | sync-manager | skill-tracker |
| 統計 skill 使用 | usage-analyst | - |
| 完整健檢 | 全部 agents | coordinator 整合 |

### 派工決策樹

```
使用者輸入 → 意圖分析
  │
  ├─ "check updates" / "outdated"
  │   → skill-tracker
  │
  ├─ "find new" / "discover" / "explore"
  │   → skill-scout
  │
  ├─ "organize" / "clean up" / "tidy"
  │   → file-organizer
  │
  ├─ "sync" / "update all"
  │   → sync-manager
  │
  ├─ "stats" / "usage" / "report"
  │   → usage-analyst
  │
  └─ "health check" / "audit" / "full scan"
      → 順序派工：
         1. file-organizer
         2. skill-tracker
         3. usage-analyst
         4. coordinator 整合報告
```

### 任務狀態追蹤

```json
{
  "task_id": "task-20260208-001",
  "type": "health-check",
  "status": "in-progress",
  "created_at": "2026-02-08T10:00:00Z",
  "assigned_agents": [
    {
      "name": "file-organizer",
      "status": "completed",
      "started_at": "2026-02-08T10:00:05Z",
      "completed_at": "2026-02-08T10:02:30Z",
      "result": "success"
    },
    {
      "name": "skill-tracker",
      "status": "in-progress",
      "started_at": "2026-02-08T10:02:35Z"
    }
  ],
  "results": {}
}
```

## 範例

### 意圖解析

```bash
parse_user_intent() {
  local input="$1"

  # 轉小寫並移除標點
  input=$(echo "$input" | tr '[:upper:]' '[:lower:]' | tr -d '.,!?')

  # 關鍵字匹配
  if [[ "$input" =~ (check|outdated|update|version) ]]; then
    echo "check-updates"
  elif [[ "$input" =~ (find|discover|explore|new|available) ]]; then
    echo "discover-skills"
  elif [[ "$input" =~ (organize|clean|tidy|structure) ]]; then
    echo "organize-files"
  elif [[ "$input" =~ (sync|pull|fetch) ]]; then
    echo "sync-upstream"
  elif [[ "$input" =~ (stats|usage|report|analytics) ]]; then
    echo "analyze-usage"
  elif [[ "$input" =~ (health|audit|check-all|full) ]]; then
    echo "health-check"
  else
    echo "unknown"
  fi
}

# 使用範例
intent=$(parse_user_intent "Check if any skills are outdated")
echo "Intent: $intent"  # 輸出: check-updates
```

### 派工執行

```bash
dispatch_task() {
  local intent="$1"

  case "$intent" in
    check-updates)
      echo "📋 Dispatching to skill-tracker..."
      # 呼叫 skill-tracker agent
      ;;
    discover-skills)
      echo "📋 Dispatching to skill-scout..."
      # 呼叫 skill-scout agent
      ;;
    organize-files)
      echo "📋 Dispatching to file-organizer..."
      # 呼叫 file-organizer agent
      ;;
    sync-upstream)
      echo "📋 Dispatching to sync-manager..."
      # 呼叫 sync-manager agent
      ;;
    analyze-usage)
      echo "📋 Dispatching to usage-analyst..."
      # 呼叫 usage-analyst agent
      ;;
    health-check)
      echo "📋 Dispatching health check sequence..."
      dispatch_health_check
      ;;
    *)
      echo "❓ Unknown intent: $intent"
      echo "Available commands:"
      echo "  - check updates"
      echo "  - find new skills"
      echo "  - organize files"
      echo "  - sync upstream"
      echo "  - usage stats"
      echo "  - health check"
      ;;
  esac
}
```

### Health Check 流程

```bash
dispatch_health_check() {
  local task_id="task-$(date +%Y%m%d-%H%M%S)"

  echo "🏥 Starting health check: $task_id"
  echo ""

  # Step 1: 整理檔案結構
  echo "📁 [1/3] Organizing file structure..."
  # 呼叫 file-organizer
  # 記錄結果

  # Step 2: 檢查 skill 更新
  echo "🔍 [2/3] Checking skill updates..."
  # 呼叫 skill-tracker
  # 記錄結果

  # Step 3: 統計使用狀況
  echo "📊 [3/3] Analyzing usage..."
  # 呼叫 usage-analyst
  # 記錄結果

  # Step 4: 整合報告
  echo ""
  echo "📄 Generating health report..."
  generate_health_report "$task_id"
}

generate_health_report() {
  local task_id="$1"

  cat << EOF
╔════════════════════════════════════════╗
║   DopeMAN Health Report          ║
╚════════════════════════════════════════╝

Task ID: $task_id
Generated: $(date)

┌─ File Organization ─────────────────────
│ ✅ All files in correct locations
│ 📊 6 agents, 12 skills, 8 rules
└─────────────────────────────────────────

┌─ Skill Updates ─────────────────────────
│ ✅ 10 skills up-to-date
│ ⚠️  2 skills have updates available
│ 📋 Outdated: version-comparison, file-classification
└─────────────────────────────────────────

┌─ Usage Statistics ──────────────────────
│ 📈 Most used: github-api-operations (42 times)
│ 📉 Least used: user-confirmation (3 times)
│ 📅 Last activity: 2026-02-08
└─────────────────────────────────────────

Overall Status: ✅ HEALTHY

Recommendations:
  1. Update 2 outdated skills
  2. Consider removing unused custom skills
  3. Backup skills_registry.json

EOF
}
```

### 錯誤處理

```bash
handle_agent_failure() {
  local agent_name="$1"
  local error_message="$2"

  echo "❌ Agent failed: $agent_name"
  echo "Error: $error_message"
  echo ""

  # 記錄到 registry
  jq ".last_error = {
    \"agent\": \"$agent_name\",
    \"message\": \"$error_message\",
    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
  }" skills_registry.json > skills_registry.json.tmp \
    && mv skills_registry.json.tmp skills_registry.json

  # 決定是否繼續或中止
  echo "Continue with other agents? (y/N): "
  read -r response

  case "$response" in
    [yY])
      return 0
      ;;
    *)
      echo "❌ Task aborted"
      return 1
      ;;
  esac
}
```

## 輸出格式

### 派工通知

```
📋 Dispatching Task

Intent: check-updates
Assigned to: skill-tracker
Priority: normal
Estimated time: 2-5 minutes

Starting...
```

### 進度更新

```
⏳ Task in progress: check-updates

[=========>              ] 45%
Current: Checking github-api-operations (6/12)
```

### 完成報告

```
✅ Task completed: check-updates

Duration: 3m 42s
Results:
  - 10 skills checked
  - 2 updates available
  - 0 errors

See detailed report: /path/to/report.md
```

## 相關規則

- `rules/task-prioritization.md`：決定任務優先順序
- `rules/agent-communication.md`：agents 間的訊息傳遞格式
- `rules/error-escalation.md`：何時中止任務、何時繼續
- `rules/no-silent-failures.md`：所有錯誤必須記錄並回報
