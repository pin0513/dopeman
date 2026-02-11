/**
 * DopeMAN Dashboard - State Management
 * 狀態管理模組
 */

const DashboardState = {
  // 應用程式資料
  data: null,

  // 當前狀態
  currentTab: 'overview',
  currentView: 'tree',
  selectedCategory: null,
  selectedItem: null,

  // UI 狀態
  loading: false,
  error: null,
  toasts: [],

  // 編輯器設定
  editorTools: null,
  defaultEditor: 'vscode',

  /**
   * 初始化狀態
   */
  init() {
    this.loadFromStorage();
    return this;
  },

  /**
   * 從 localStorage 載入設定
   */
  loadFromStorage() {
    try {
      const savedEditor = localStorage.getItem(DashboardConfig.STORAGE_KEYS.DEFAULT_EDITOR);
      const savedTab = localStorage.getItem(DashboardConfig.STORAGE_KEYS.LAST_ACTIVE_TAB);
      const savedTools = localStorage.getItem(DashboardConfig.STORAGE_KEYS.EDITOR_TOOLS);

      if (savedEditor) this.defaultEditor = savedEditor;
      if (savedTab) this.currentTab = savedTab;
      if (savedTools) this.editorTools = JSON.parse(savedTools);
    } catch (error) {
      console.error('Failed to load from storage:', error);
    }
  },

  /**
   * 儲存到 localStorage
   */
  saveToStorage() {
    try {
      localStorage.setItem(DashboardConfig.STORAGE_KEYS.DEFAULT_EDITOR, this.defaultEditor);
      localStorage.setItem(DashboardConfig.STORAGE_KEYS.LAST_ACTIVE_TAB, this.currentTab);
      if (this.editorTools) {
        localStorage.setItem(
          DashboardConfig.STORAGE_KEYS.EDITOR_TOOLS,
          JSON.stringify(this.editorTools)
        );
      }
    } catch (error) {
      console.error('Failed to save to storage:', error);
    }
  },

  /**
   * 設定資料
   */
  setData(data) {
    this.data = data;
    this.updateEditorTools();
    return this;
  },

  /**
   * 更新編輯器工具設定
   */
  updateEditorTools() {
    if (this.data && this.data.user_preferences && this.data.user_preferences.editor_tools) {
      this.editorTools = this.data.user_preferences.editor_tools;
      this.defaultEditor = this.data.user_preferences.default_editor || 'vscode';
    }
  },

  /**
   * 切換 Tab
   */
  switchTab(tabId) {
    this.currentTab = tabId;
    this.saveToStorage();
    return this;
  },

  /**
   * 切換視圖
   */
  switchView(viewId) {
    this.currentView = viewId;
    return this;
  },

  /**
   * 選擇類別
   */
  selectCategory(categoryId) {
    this.selectedCategory = categoryId;
    this.selectedItem = null;
    return this;
  },

  /**
   * 選擇項目
   */
  selectItem(item) {
    this.selectedItem = item;
    return this;
  },

  /**
   * 設定載入狀態
   */
  setLoading(loading) {
    this.loading = loading;
    return this;
  },

  /**
   * 設定錯誤
   */
  setError(error) {
    this.error = error;
    return this;
  },

  /**
   * 清除錯誤
   */
  clearError() {
    this.error = null;
    return this;
  },

  /**
   * 新增 Toast 通知
   */
  addToast(message, type = 'info') {
    const toast = {
      id: Date.now(),
      message,
      type,
      timestamp: new Date()
    };

    this.toasts.push(toast);

    // 限制最多顯示數量
    if (this.toasts.length > DashboardConfig.UI.MAX_TOAST_VISIBLE) {
      this.toasts.shift();
    }

    // 自動移除
    setTimeout(() => {
      this.removeToast(toast.id);
    }, DashboardConfig.UI.TOAST_DURATION);

    return toast;
  },

  /**
   * 移除 Toast 通知
   */
  removeToast(toastId) {
    this.toasts = this.toasts.filter(t => t.id !== toastId);
    return this;
  },

  /**
   * 取得統計資訊
   */
  getStats() {
    if (!this.data || !this.data.categories) {
      return null;
    }

    return {
      totalSkills:
        (this.data.categories.global_skills?.count || 0) +
        (this.data.categories.project_skills?.count || 0) +
        (this.data.categories.dev_skills?.count || 0),
      totalAgents: this.data.categories.agents?.count || 0,
      totalRules:
        (this.data.categories.global_rules?.count || 0) +
        (this.data.categories.project_rules?.count || 0),
      totalCommands: this.data.categories.commands?.count || 0,
      lastScan: this.data.last_scan || null
    };
  },

  /**
   * 取得類別資料
   */
  getCategoryData(categoryId) {
    if (!this.data || !this.data.categories) {
      return null;
    }
    return this.data.categories[categoryId] || null;
  },

  /**
   * 取得圖層資料
   */
  getLayerData(layerId) {
    if (!this.data || !this.data.layers) {
      return null;
    }
    return this.data.layers[layerId] || null;
  }
};

// 初始化
DashboardState.init();

// 掛載到 window
if (typeof window !== 'undefined') {
  window.DashboardState = DashboardState;
}

// 導出模組
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DashboardState;
}
