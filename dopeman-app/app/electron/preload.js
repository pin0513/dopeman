import { contextBridge, ipcRenderer } from 'electron';

/**
 * Preload script for DopeMAN
 * Exposes safe APIs to the renderer process
 */

contextBridge.exposeInMainWorld('dopeman', {
  // 版本資訊
  version: '2.1.1',

  // 平台資訊
  platform: process.platform,

  // 未來可擴展的 API
  // 例如：通知、檔案選擇、系統對話框等
});

console.log('[DopeMAN Preload] Preload script loaded');
