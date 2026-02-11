/**
 * DopeMAN Dashboard - Configuration
 * 設定與常數定義
 */

const DashboardConfig = {
  // API 端點
  API: {
    BASE_URL: '',
    ENDPOINTS: {
      DATA: '/control-center-real-data.json',
      HEALTH_CHECK: '/api/health-check',
      INSTALL_OFFICIAL: '/api/install-official',
      UNINSTALL_OFFICIAL: '/api/uninstall-official',
      UPDATE_OFFICIAL: '/api/update-official'
    }
  },

  // 圖層類型
  LAYER_TYPES: {
    ENTRY: {
      id: 'entry',
      label: '入口層',
      emoji: '🚪',
      description: 'Skills & Commands'
    },
    COORDINATION: {
      id: 'coordination',
      label: '協調層',
      emoji: '🎯',
      description: 'Coordinators'
    },
    EXECUTION: {
      id: 'execution',
      label: '執行層',
      emoji: '⚙️',
      description: 'Workers & Sub-skills'
    }
  },

  // 類別設定
  CATEGORIES: {
    GLOBAL_SKILLS: {
      id: 'global_skills',
      label: '全域 Skills',
      icon: '🌐',
      color: '#3b82f6'
    },
    PROJECT_SKILLS: {
      id: 'project_skills',
      label: '專案 Skills',
      icon: '📦',
      color: '#8b5cf6'
    },
    DEV_SKILLS: {
      id: 'dev_skills',
      label: '開發中 Skills',
      icon: '🔧',
      color: '#f59e0b'
    },
    AGENTS: {
      id: 'agents',
      label: 'Agents',
      icon: '🤖',
      color: '#10b981'
    },
    RULES: {
      id: 'global_rules',
      label: 'Rules',
      icon: '📋',
      color: '#ef4444'
    },
    COMMANDS: {
      id: 'commands',
      label: 'Commands',
      icon: '⚡',
      color: '#ec4899'
    }
  },

  // 編輯器工具設定
  EDITOR_TOOLS: {
    VSCODE: {
      id: 'vscode',
      name: 'VS Code',
      protocol: 'vscode://',
      icon: '📝',
      enabled: true
    },
    CURSOR: {
      id: 'cursor',
      name: 'Cursor',
      protocol: 'cursor://',
      icon: '✨',
      enabled: true
    },
    WINDSURF: {
      id: 'windsurf',
      name: 'Windsurf',
      protocol: 'windsurf://',
      icon: '🏄',
      enabled: false
    }
  },

  // UI 設定
  UI: {
    ANIMATION_DURATION: 300,
    TOAST_DURATION: 3000,
    MAX_TOAST_VISIBLE: 3,
    TREE_INDENT: 20
  },

  // 本地儲存鍵
  STORAGE_KEYS: {
    DEFAULT_EDITOR: 'dopeman_default_editor',
    EDITOR_TOOLS: 'dopeman_editor_tools',
    LAST_ACTIVE_TAB: 'dopeman_last_active_tab',
    THEME: 'dopeman_theme'
  },

  // 路徑常數
  PATHS: {
    HOME: '/Users/paul_huang',
    CLAUDE_DIR: '~/.claude',
    SKILLS_DIR: '~/.claude/skills',
    AGENTS_DIR: '~/.claude/agents',
    RULES_DIR: '~/.claude/rules',
    COMMANDS_DIR: '~/.claude/commands'
  }
};

// 如果在瀏覽器環境，掛載到 window
if (typeof window !== 'undefined') {
  window.DashboardConfig = DashboardConfig;
}

// 如果在 Node.js 環境，導出模組
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DashboardConfig;
}
