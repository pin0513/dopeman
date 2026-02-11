/**
 * DopeMAN Dashboard - API Module
 * API 呼叫與資料載入
 */

const DashboardAPI = {
  /**
   * 載入 Dashboard 資料
   */
  async loadData() {
    try {
      DashboardState.setLoading(true).clearError();

      const response = await fetch(DashboardConfig.API.ENDPOINTS.DATA);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      DashboardState.setData(data).setLoading(false);

      return data;
    } catch (error) {
      console.error('Failed to load data:', error);
      DashboardState.setError(error.message).setLoading(false);
      throw error;
    }
  },

  /**
   * 健康檢查
   */
  async healthCheck() {
    try {
      const response = await fetch(DashboardConfig.API.ENDPOINTS.HEALTH_CHECK);
      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },

  /**
   * 安裝官方 Skill/Team
   */
  async installOfficial(itemId) {
    try {
      DashboardState.addToast('開始安裝...', 'info');

      const response = await fetch(DashboardConfig.API.ENDPOINTS.INSTALL_OFFICIAL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId })
      });

      const result = await response.json();

      if (result.status === 'success') {
        DashboardState.addToast('安裝成功！', 'success');
      } else {
        throw new Error(result.message || '安裝失敗');
      }

      return result;
    } catch (error) {
      console.error('Install failed:', error);
      DashboardState.addToast(error.message, 'error');
      throw error;
    }
  },

  /**
   * 移除官方 Skill/Team
   */
  async uninstallOfficial(itemId) {
    try {
      DashboardState.addToast('開始移除...', 'info');

      const response = await fetch(DashboardConfig.API.ENDPOINTS.UNINSTALL_OFFICIAL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId })
      });

      const result = await response.json();

      if (result.status === 'success') {
        DashboardState.addToast('移除成功！', 'success');
      } else {
        throw new Error(result.message || '移除失敗');
      }

      return result;
    } catch (error) {
      console.error('Uninstall failed:', error);
      DashboardState.addToast(error.message, 'error');
      throw error;
    }
  },

  /**
   * 更新官方 Skill/Team
   */
  async updateOfficial(itemId) {
    try {
      DashboardState.addToast('開始更新...', 'info');

      const response = await fetch(DashboardConfig.API.ENDPOINTS.UPDATE_OFFICIAL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId })
      });

      const result = await response.json();

      if (result.status === 'success') {
        DashboardState.addToast('更新成功！', 'success');
      } else {
        throw new Error(result.message || '更新失敗');
      }

      return result;
    } catch (error) {
      console.error('Update failed:', error);
      DashboardState.addToast(error.message, 'error');
      throw error;
    }
  }
};

// 掛載到 window
if (typeof window !== 'undefined') {
  window.DashboardAPI = DashboardAPI;
}

// 導出模組
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DashboardAPI;
}
