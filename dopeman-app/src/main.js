const { app, BrowserWindow, ipcMain, Tray, Menu } = require('electron');
const path = require('path');
const { findAvailablePort } = require('./port-detector');
const PythonServerManager = require('./python-server');

let mainWindow = null;
let tray = null;
let serverManager = null;
let httpPort = null;
let wsPort = null;

// 確保單一實例
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  console.log('⚠️  DopeMAN 已在運行中');
  app.quit();
} else {
  app.on('second-instance', (event, commandLine, workingDirectory) => {
    // 用戶嘗試開第二個實例，聚焦現有視窗
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
      mainWindow.show();
    }
  });

  app.whenReady().then(async () => {
    try {
      // 自動偵測可用端口
      console.log('🔍 偵測可用端口...');
      httpPort = await findAvailablePort(8891, 8999);
      wsPort = await findAvailablePort(httpPort + 1, 9000);

      console.log(`✅ HTTP Port: ${httpPort}`);
      console.log(`✅ WebSocket Port: ${wsPort}`);

      // 啟動 Python 伺服器
      serverManager = new PythonServerManager(httpPort, wsPort);
      await serverManager.start();

      // 建立主視窗
      createMainWindow();

      // 建立系統托盤
      createTray();

      console.log('🎉 DopeMAN 啟動完成');
    } catch (error) {
      console.error('❌ 啟動失敗:', error);
      app.quit();
    }
  });

  app.on('window-all-closed', () => {
    // macOS 上保持應用運行（托盤模式）
    if (process.platform !== 'darwin') {
      app.quit();
    }
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    }
  });

  app.on('before-quit', () => {
    // 清理資源
    if (serverManager) {
      serverManager.stop();
    }
  });
}

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    title: 'DopeMAN - Skills Control Center',
    icon: path.join(__dirname, '../assets/icon.png'),
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, 'preload.js')
    },
    backgroundColor: '#667eea',
    show: false // 先隱藏，載入完成後再顯示
  });

  // 載入 Dashboard
  mainWindow.loadURL(`http://localhost:${httpPort}/control-center-real.html`);

  // 視窗載入完成後顯示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // 視窗關閉時最小化到托盤（而非退出）
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  // 開發模式下開啟 DevTools
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }
}

function createTray() {
  // 使用簡單的圖示（之後會替換為實際圖示）
  const trayIcon = path.join(__dirname, '../assets/tray-icon.png');

  tray = new Tray(trayIcon);

  const contextMenu = Menu.buildFromTemplate([
    {
      label: '開啟 Dashboard',
      click: () => {
        mainWindow.show();
        mainWindow.loadURL(`http://localhost:${httpPort}/control-center-real.html`);
      }
    },
    {
      label: '任務監控',
      click: () => {
        mainWindow.show();
        mainWindow.loadURL(`http://localhost:${httpPort}/task-monitor.html`);
      }
    },
    { type: 'separator' },
    {
      label: '重新掃描',
      click: async () => {
        try {
          await serverManager.triggerScan();
          console.log('✅ 掃描完成');
        } catch (error) {
          console.error('❌ 掃描失敗:', error);
        }
      }
    },
    {
      label: '健康檢查',
      click: async () => {
        try {
          await serverManager.triggerHealthCheck();
          console.log('✅ 健康檢查完成');
        } catch (error) {
          console.error('❌ 健康檢查失敗:', error);
        }
      }
    },
    { type: 'separator' },
    {
      label: `端口資訊`,
      enabled: false
    },
    {
      label: `  HTTP: ${httpPort}`,
      enabled: false
    },
    {
      label: `  WebSocket: ${wsPort}`,
      enabled: false
    },
    { type: 'separator' },
    {
      label: '結束',
      click: () => {
        app.isQuitting = true;
        app.quit();
      }
    }
  ]);

  tray.setContextMenu(contextMenu);
  tray.setToolTip('DopeMAN Control Center');

  // 點擊托盤圖示顯示主視窗
  tray.on('click', () => {
    if (mainWindow.isVisible()) {
      mainWindow.hide();
    } else {
      mainWindow.show();
    }
  });
}

// IPC 處理
ipcMain.handle('get-ports', () => {
  return { httpPort, wsPort };
});

ipcMain.handle('scan-skills', async () => {
  return await serverManager.triggerScan();
});

ipcMain.handle('health-check', async () => {
  return await serverManager.triggerHealthCheck();
});
