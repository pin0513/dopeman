import { app, BrowserWindow } from 'electron';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { startAll, stopAll, checkPythonEnv } from './process-manager.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

let mainWindow = null;

/**
 * 取得資源路徑
 * 開發模式：../commands/
 * 打包後：Resources/commands/
 */
function getResourcePath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'commands');
  }
  return path.join(__dirname, '../../commands');
}

/**
 * 載入配置檔
 */
function loadConfig() {
  return {
    http: {
      port: 8891,
      host: '127.0.0.1'
    },
    websocket: {
      port: 8892,
      host: '127.0.0.1'
    },
    dashboard: {
      url: 'control-center-real.html'
    }
  };
}

/**
 * 創建主視窗
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    title: 'DopeMAN - Skills Control Center',
    backgroundColor: '#1a1a2e',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      webSecurity: true
    },
    show: false
  });

  // 視窗準備好後才顯示（避免閃爍）
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // 載入 Dashboard
  const config = loadConfig();
  const dashboardURL = `http://${config.http.host}:${config.http.port}/${config.dashboard.url}`;

  // 等待伺服器啟動後載入
  setTimeout(() => {
    mainWindow.loadURL(dashboardURL);
  }, 2000);

  // 開發模式：開啟 DevTools
  if (!app.isPackaged) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

/**
 * 應用程式準備完成
 */
app.whenReady().then(async () => {
  console.log('[DopeMAN] App is ready');
  console.log('[DopeMAN] Resource path:', getResourcePath());

  // 檢查 Python 環境
  const pythonCheck = await checkPythonEnv(getResourcePath());
  if (!pythonCheck.success) {
    console.error('[DopeMAN] Python environment check failed:', pythonCheck.error);
    app.quit();
    return;
  }

  console.log('[DopeMAN] Python environment OK');
  console.log('[DopeMAN] Python version:', pythonCheck.version);
  console.log('[DopeMAN] Dependencies:', pythonCheck.dependencies);

  // 啟動後端服務
  try {
    await startAll(getResourcePath());
    console.log('[DopeMAN] Backend services started');
  } catch (error) {
    console.error('[DopeMAN] Failed to start backend services:', error);
    app.quit();
    return;
  }

  // 創建視窗
  createWindow();
});

/**
 * 所有視窗關閉
 */
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

/**
 * 重新激活（macOS）
 */
app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

/**
 * 應用程式退出前
 */
app.on('before-quit', async () => {
  console.log('[DopeMAN] Stopping backend services...');
  await stopAll();
  console.log('[DopeMAN] Backend services stopped');
});

/**
 * 處理未捕獲的異常
 */
process.on('uncaughtException', (error) => {
  console.error('[DopeMAN] Uncaught exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('[DopeMAN] Unhandled rejection at:', promise, 'reason:', reason);
});
