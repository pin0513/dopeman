# Extended Scan Specification - Commands, Rules, Agents

## 核心設計理念

### 避免循環參考的策略

**問題**：
```
Skill A → depends on → Skill B
Skill B → depends on → Skill C
Skill C → depends on → Skill A  ❌ 循環！

Agent A → uses → Skill X
Skill X → used by → Agent A
Skill X → depends on → Skill Y
Skill Y → used by → Agent B  🤔 關係發散
```

**解決方案**：採用**分層視角（Layered View）**

```
📍 入口層（Entry Layer）
  ├─ Commands - 用戶輸入的指令
  └─ Skills (Root) - 主要技能入口

📍 協調層（Coordination Layer）
  ├─ Team Coordinators - 團隊協調者
  └─ Skill Orchestrators - 技能編排者

📍 執行層（Execution Layer）
  ├─ Agents - 執行者
  ├─ Sub-skills - 子技能
  └─ Rules - 規則約束

📍 資源層（Resource Layer）
  ├─ Tools - 工具函數
  └─ Data - 資料檔案
```

---

## 1. Commands 掃描

### 1.1 Command 定義

**Command 類型**：

```typescript
interface Command {
  name: string;                    // 指令名稱 (如 "check-updates")
  entry_point: string;             // 入口 skill (如 "dopeman")
  syntax: string;                  // 語法 (如 "/dopeman check-updates")
  description: string;             // 功能描述
  delegates_to: string[];          // 委派給哪些 agents
  uses_skills: string[];           // 使用哪些 skills
  applies_rules: string[];         // 套用哪些 rules
  examples: string[];              // 使用範例
}
```

### 1.2 掃描策略

**掃描位置**：
- `~/.claude/skills/*/commands/` - 技能定義的命令
- `~/DEV/projects/*/commands/` - 專案定義的命令
- `.claude/skills/*/SKILL.md` - 從 skill 文件提取

**解析方式**：
```markdown
## Commands

### check-updates

檢查 skills 更新

**語法**：
```bash
/dopeman check-updates
```

**流程**：
1. coordinator 啟動
2. 委派給 skill-tracker
3. 套用 respect-rate-limits rule
4. 回報結果

**範例**：
```bash
/dopeman check-updates
```
```

**輸出資料**：
```json
{
  "name": "check-updates",
  "full_command": "/dopeman check-updates",
  "entry_skill": "dopeman",
  "coordinator": "dopeman-coordinator",
  "delegates_to": ["skill-tracker"],
  "uses_skills": ["github-api-operations"],
  "applies_rules": ["respect-rate-limits", "log-all-actions"],
  "level": "entry"
}
```

### 1.3 Command 視圖

**按入口分組**：
```
📍 Entry Commands

/dopeman
  ├─ check-updates → skill-tracker
  ├─ organize → file-organizer
  ├─ export-config → sync-manager
  └─ control-center → control-center-ui

/team001
  ├─ dev-workflow → dev-team-lead
  └─ test → domain-qa

/slide-consult
  ├─ create → slide-coordinator
  └─ export → slide-export
```

---

## 2. Rules 掃描

### 2.1 Rule 定義

**Rule 類型**：

```typescript
interface Rule {
  name: string;                    // 規則名稱
  path: string;                    // 檔案路徑
  applicability: string[];         // 適用於哪些 agents/skills
  scope: "global" | "project";     // 全域或專案
  description: string;             // 規則描述
  violation_examples: string[];    // 違反情境
  exceptions: string[];            // 例外情況
  used_by_agents: string[];        // 哪些 agents 使用
  used_by_skills: string[];        // 哪些 skills 使用
}
```

### 2.2 掃描策略

**掃描位置**：
- `~/.claude/rules/` - 全域規則
- `~/DEV/projects/*/.claude/rules/` - 專案規則

**解析 YAML Frontmatter**：
```yaml
---
name: No Silent Failures
applicability: all agents
---
```

**輸出資料**：
```json
{
  "name": "no-silent-failures",
  "path": "~/.claude/rules/no-silent-failures.md",
  "scope": "global",
  "applicability": ["all agents"],
  "description": "所有錯誤必須明確記錄與通知",
  "used_by_agents": ["coordinator", "file-organizer", "skill-tracker"],
  "used_by_skills": ["dopeman"],
  "violation_count": 0
}
```

### 2.3 Rules 視圖

**按適用範圍分組**：
```
📍 Global Rules (全域)

🌍 所有 Agents
  ├─ no-silent-failures
  ├─ backup-before-modify
  ├─ idempotent-operations
  └─ log-all-actions

🎯 特定 Agents
  ├─ skill-tracker, skill-scout
  │   └─ respect-rate-limits
  └─ file-organizer
      └─ backup-before-modify

📁 Project Rules (專案)

~/DEV/MAYO-Report-Master
  ├─ team001-mayo-coding-standard
  ├─ team001-e2e-test-design
  └─ azure-devops-npm-auth
```

**按使用者反向查詢**：
```
dopeman skill
  ├─ Uses rules:
  │   ├─ no-silent-failures (global)
  │   ├─ backup-before-modify (global)
  │   └─ log-all-actions (global)
  └─ Agents under this skill:
      ├─ coordinator
      │   └─ Uses: no-silent-failures, log-all-actions
      ├─ skill-tracker
      │   └─ Uses: respect-rate-limits, log-all-actions
      └─ file-organizer
          └─ Uses: backup-before-modify, no-silent-failures
```

---

## 3. Agents 掃描

### 3.1 Agent 定義

**Agent 類型**：

```typescript
interface Agent {
  name: string;                    // Agent 名稱
  path: string;                    // 檔案路徑
  type: "coordinator" | "worker";  // 協調者或執行者
  belongs_to_skill: string | null; // 屬於哪個 skill（如果是 team agent）
  uses_skills: string[];           // 使用哪些 skills
  applies_rules: string[];         // 套用哪些 rules
  delegates_to: string[];          // 委派給哪些 agents
  delegated_by: string[];          // 被誰委派
  scope: "global" | "project";     // 全域或專案
}
```

### 3.2 掃描策略

**掃描位置**：
- `~/.claude/agents/` - 全域 agents（如果有）
- `~/DEV/projects/*/.claude/agents/` - 專案 agents

**解析規則**：
1. 檢查檔案結構：`agents/coordinator.md` → type = coordinator
2. 檢查檔案位置：`agents/group/worker.md` → type = worker
3. 解析 SKILL.md：找出 `belongs_to_skill`

**輸出資料**：
```json
{
  "name": "dopeman-coordinator",
  "path": "~/DEV/projects/dopeman/.claude/agents/coordinator.md",
  "type": "coordinator",
  "belongs_to_skill": "dopeman",
  "uses_skills": [],
  "applies_rules": ["no-silent-failures", "log-all-actions"],
  "delegates_to": [
    "file-organizer",
    "skill-tracker",
    "skill-scout",
    "usage-analyst",
    "sync-manager"
  ],
  "delegated_by": [],
  "scope": "project"
}
```

### 3.3 Agents 視圖

**協調者視角（Coordinator View）**：

```
📍 dopeman (Coordinator)
  │
  ├─ 🎯 Delegates to:
  │   ├─ file-organizer
  │   │   ├─ Uses skills: (none)
  │   │   └─ Applies rules: backup-before-modify, no-silent-failures
  │   ├─ skill-tracker
  │   │   ├─ Uses skills: github-api-operations
  │   │   └─ Applies rules: respect-rate-limits, log-all-actions
  │   ├─ skill-scout
  │   │   ├─ Uses skills: github-api-operations
  │   │   └─ Applies rules: respect-rate-limits
  │   ├─ usage-analyst
  │   │   └─ Uses skills: (none)
  │   └─ sync-manager
  │       └─ Uses skills: (none)
  │
  └─ 📋 Applied rules:
      ├─ no-silent-failures
      └─ log-all-actions
```

**技能入口視角（Skill Entry View）**：

```
📍 team001 (Skill Entry)
  │
  ├─ 🎯 Coordinator:
  │   └─ dev-team-lead
  │       ├─ Delegates to:
  │       │   ├─ dev-team-pm
  │       │   ├─ dev-team-architect
  │       │   ├─ dev-team-ui
  │       │   ├─ dev-team-backend
  │       │   ├─ dev-team-frontend
  │       │   ├─ dev-team-devops
  │       │   └─ dev-team-qa
  │       └─ Applies rules:
  │           ├─ spec-before-dev
  │           ├─ test-before-merge
  │           └─ code-review-required
  │
  ├─ 📋 Shared rules:
  │   ├─ team001-mayo-coding-standard
  │   ├─ team001-git-workflow
  │   └─ team001-deployment-checklist
  │
  └─ 🔗 Depends on skills:
      └─ (none)
```

---

## 4. 整合視圖（Integrated View）

### 4.1 完整分層視圖

```
┌─────────────────────────────────────────────────────────┐
│                📍 Entry Layer (入口層)                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Commands:                                              │
│  ├─ /dopeman check-updates                        │
│  ├─ /team001 dev-workflow                               │
│  └─ /slide-consult create                               │
│                                                          │
│  Root Skills:                                           │
│  ├─ dopeman                                       │
│  ├─ team001                                             │
│  └─ slide-consult                                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│             📍 Coordination Layer (協調層)               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  dopeman                                          │
│  └─ dopeman-coordinator                           │
│      ├─ Applies: no-silent-failures, log-all-actions   │
│      └─ Delegates to: ↓                                │
│                                                          │
│  team001                                                │
│  └─ dev-team-lead                                       │
│      ├─ Applies: spec-before-dev, code-review-required │
│      └─ Delegates to: ↓                                │
│                                                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              📍 Execution Layer (執行層)                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  dopeman Workers:                                 │
│  ├─ file-organizer                                      │
│  │   └─ Applies: backup-before-modify                  │
│  ├─ skill-tracker                                       │
│  │   ├─ Uses: github-api-operations                    │
│  │   └─ Applies: respect-rate-limits                   │
│  └─ skill-scout                                         │
│      └─ Uses: github-api-operations                    │
│                                                          │
│  team001 Workers:                                       │
│  ├─ dev-team-pm                                         │
│  ├─ dev-team-backend                                    │
│  └─ dev-team-qa                                         │
│                                                          │
│  Sub-skills:                                            │
│  ├─ github-api-operations                               │
│  └─ shared-utilities                                    │
│                                                          │
│  Rules:                                                 │
│  ├─ Global:                                             │
│  │   ├─ no-silent-failures                             │
│  │   ├─ backup-before-modify                           │
│  │   └─ respect-rate-limits                            │
│  └─ Project:                                            │
│      ├─ team001-mayo-coding-standard                   │
│      └─ azure-devops-npm-auth                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 4.2 溯源路徑（Traceability Path）

**從 Command 到 Execution 的完整路徑**：

```
用戶輸入：
  /dopeman check-updates

↓ 入口

Entry Skill:
  dopeman

↓ 協調

Coordinator:
  dopeman-coordinator
  └─ Applies rules:
      ├─ no-silent-failures
      └─ log-all-actions

↓ 委派

Worker Agent:
  skill-tracker
  ├─ Uses skills:
  │   └─ github-api-operations
  └─ Applies rules:
      ├─ respect-rate-limits
      └─ log-all-actions

↓ 執行

Sub-skill:
  github-api-operations
  └─ Applies rules:
      └─ respect-rate-limits

↓ 結果

回傳給 coordinator → 回報用戶
```

---

## 5. 避免循環參考的機制

### 5.1 分層規則

**強制規則**：
```
Entry Layer
  ↓ can delegate to
Coordination Layer
  ↓ can delegate to
Execution Layer
  ↓ can use
Resource Layer

❌ 禁止：Execution Layer → Coordination Layer
❌ 禁止：Resource Layer → Execution Layer
```

### 5.2 循環偵測

**偵測算法**：
```typescript
function detectCycle(graph: DependencyGraph): Cycle[] {
  const visited = new Set<string>();
  const recStack = new Set<string>();
  const cycles: Cycle[] = [];

  function dfs(node: string, path: string[]) {
    visited.add(node);
    recStack.add(node);
    path.push(node);

    for (const neighbor of graph.get(node)) {
      if (!visited.has(neighbor)) {
        dfs(neighbor, path);
      } else if (recStack.has(neighbor)) {
        // 找到循環
        const cycleStart = path.indexOf(neighbor);
        cycles.push({
          path: path.slice(cycleStart),
          severity: "error"
        });
      }
    }

    recStack.delete(node);
    path.pop();
  }

  return cycles;
}
```

**輸出範例**：
```
⚠️  Cycle Detected:

  Skill A → Skill B → Skill C → Skill A

  建議：
  - 拆分 Skill C，移除對 Skill A 的依賴
  - 或建立 shared-utils skill，讓 A, B, C 都依賴它
```

### 5.3 依賴深度限制

**限制規則**：
```
Max Dependency Depth = 5

Entry Skill (depth 0)
  → Coordinator (depth 1)
    → Worker Agent (depth 2)
      → Sub-skill (depth 3)
        → Utility (depth 4)
          → Library (depth 5) ✓

          → Another Sub-skill (depth 6) ❌ 超過限制！
```

**檢查結果**：
```
⚠️  Dependency Depth Exceeded:

  Path: dopeman → coordinator → skill-tracker
        → github-api-operations → http-client
        → retry-logic → backoff-strategy

  Depth: 6 (Max: 5)

  建議：合併 retry-logic 與 backoff-strategy
```

---

## 6. 資料結構設計

### 6.1 完整資料模型

```typescript
interface ControlCenterData {
  version: string;
  last_scan: string;

  // 四大類別
  commands: Command[];
  rules: Rule[];
  agents: Agent[];
  skills: Skill[];

  // 關聯關係
  relationships: {
    command_to_skill: Map<string, string>;
    skill_to_coordinator: Map<string, string>;
    coordinator_to_workers: Map<string, string[]>;
    agent_to_skills: Map<string, string[]>;
    agent_to_rules: Map<string, string[]>;
    skill_to_subskills: Map<string, string[]>;
  };

  // 分層視圖
  layers: {
    entry: {
      commands: string[];
      root_skills: string[];
    };
    coordination: {
      coordinators: string[];
    };
    execution: {
      workers: string[];
      sub_skills: string[];
      rules: string[];
    };
    resource: {
      tools: string[];
      data: string[];
    };
  };

  // 問題偵測
  issues: {
    cycles: Cycle[];
    depth_violations: DepthViolation[];
    missing_dependencies: MissingDependency[];
    orphaned_items: OrphanedItem[];
  };
}
```

### 6.2 儲存位置

```
~/.claude/memory/dopeman/
├── control-center-data.json       ← 主要資料
├── commands-index.json            ← Commands 索引
├── rules-index.json               ← Rules 索引
├── agents-index.json              ← Agents 索引
├── dependency-graph.json          ← 依賴圖譜
└── layer-view.json                ← 分層視圖
```

---

## 7. 掃描流程

### 7.1 完整掃描流程

```
Start
  ↓
[1] 掃描 Skills
  ├─ Global skills
  ├─ Project skills
  ├─ Development skills
  └─ Candidate skills
  ↓
[2] 掃描 Agents
  ├─ 識別 coordinators
  ├─ 識別 workers
  └─ 建立 delegation 關係
  ↓
[3] 掃描 Rules
  ├─ Global rules
  ├─ Project rules
  └─ 解析 applicability
  ↓
[4] 掃描 Commands
  ├─ 從 SKILL.md 提取
  └─ 從 commands/ 目錄提取
  ↓
[5] 建立關聯
  ├─ Command → Skill
  ├─ Skill → Coordinator
  ├─ Coordinator → Workers
  ├─ Agent → Skills
  ├─ Agent → Rules
  └─ Skill → Sub-skills
  ↓
[6] 分層分類
  ├─ Entry Layer
  ├─ Coordination Layer
  ├─ Execution Layer
  └─ Resource Layer
  ↓
[7] 問題偵測
  ├─ 循環偵測
  ├─ 深度檢查
  ├─ 缺失依賴
  └─ 孤立項目
  ↓
[8] 生成報告
  ├─ JSON 資料
  ├─ Markdown 報告
  └─ HTML 互動視圖
  ↓
End
```

### 7.2 增量掃描

**條件**：
- 上次掃描 < 1 小時
- 且檔案系統無變更

**策略**：
```
IF cache_valid THEN
  載入快取
  只掃描變更的檔案
  合併結果
ELSE
  完整掃描
  更新快取
END IF
```

---

## 8. 視覺化設計

### 8.1 互動式樹狀圖

**使用 blessed-contrib**：

```javascript
const tree = contrib.tree({
  label: 'Skills Control Center',
  template: {
    lines: true
  },
  style: {
    fg: 'green'
  }
});

const data = {
  extended: true,
  children: {
    '📍 Entry Layer': {
      children: {
        'Commands': { ... },
        'Root Skills': { ... }
      }
    },
    '📍 Coordination Layer': { ... },
    '📍 Execution Layer': { ... }
  }
};

tree.setData(data);
```

### 8.2 依賴圖譜（D3.js）

**HTML 報告中嵌入**：
```html
<svg id="dependency-graph"></svg>

<script>
  const nodes = [
    { id: 'dopeman', layer: 'entry' },
    { id: 'coordinator', layer: 'coordination' },
    { id: 'skill-tracker', layer: 'execution' }
  ];

  const links = [
    { source: 'dopeman', target: 'coordinator' },
    { source: 'coordinator', target: 'skill-tracker' }
  ];

  // D3.js force layout
  d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter());
</script>
```

---

## 9. 命令列介面

### 9.1 擴充命令

```bash
# 掃描所有（包含 commands, rules, agents）
/dopeman control-center scan --all

# 只掃描特定類型
/dopeman control-center scan --type=commands
/dopeman control-center scan --type=rules
/dopeman control-center scan --type=agents

# 檢視分層結構
/dopeman control-center view layers
/dopeman control-center view --layer=entry
/dopeman control-center view --layer=coordination

# 追蹤路徑
/dopeman control-center trace "/dopeman check-updates"
/dopeman control-center trace --from=command --to=execution

# 偵測問題
/dopeman control-center check cycles
/dopeman control-center check depth
/dopeman control-center check orphans
```

### 9.2 互動式視圖

```
┌─────────────────────────────────────────────┐
│  DopeMAN - Extended Control Center   │
├─────────────────────────────────────────────┤
│                                             │
│  掃描類型：                                  │
│  [✓] Skills    [✓] Agents                  │
│  [✓] Rules     [✓] Commands                │
│                                             │
│  視圖模式：                                  │
│  ( ) 分層視圖  (•) 協調者視圖               │
│  ( ) 技能入口  ( ) 依賴圖譜                 │
│                                             │
│  [掃描] [檢視] [報告] [設定] [退出]          │
│                                             │
└─────────────────────────────────────────────┘
```

---

**版本**：v1.0.0
**建立日期**：2026-02-08
**維護者**：DopeMAN Team
