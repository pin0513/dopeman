const { contextBridge, ipcRenderer } = require('electron');

/**
 * 暴露安全的 API 給前端使用
 * 這些 API 會被注入到 window.dopeman 物件中
 */
contextBridge.exposeInMainWorld('dopeman', {
  /**
   * 取得當前使用的端口資訊
   */
  getPorts: async () => {
    return await ipcRenderer.invoke('get-ports');
  },

  /**
   * 觸發技能掃描
   */
  scanSkills: async () => {
    return await ipcRenderer.invoke('scan-skills');
  },

  /**
   * 觸發健康檢查
   */
  healthCheck: async () => {
    return await ipcRenderer.invoke('health-check');
  },

  /**
   * 取得應用程式版本
   */
  getVersion: () => {
    return '1.0.0';
  },

  /**
   * 取得平台資訊
   */
  getPlatform: () => {
    return process.platform;
  }
});

// 在 DOM 載入完成後注入提示訊息
window.addEventListener('DOMContentLoaded', () => {
  console.log('🚀 DopeMAN Electron App');
  console.log('📦 Preload script loaded');
  console.log('✅ API injected to window.dopeman');
});
