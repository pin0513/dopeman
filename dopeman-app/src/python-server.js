const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class PythonServerManager {
  constructor(httpPort, wsPort) {
    this.httpPort = httpPort;
    this.wsPort = wsPort;
    this.httpProcess = null;
    this.wsProcess = null;
    this.commandsPath = this.getCommandsPath();
  }

  /**
   * 取得 commands 目錄路徑（開發模式 vs 打包後）
   */
  getCommandsPath() {
    // 開發模式：使用專案原始路徑
    const devPath = path.join(__dirname, '../../commands');
    if (fs.existsSync(devPath)) {
      return devPath;
    }

    // 打包後：使用應用程式資源路徑
    const { app } = require('electron');
    const prodPath = path.join(app.getAppPath(), 'commands');
    if (fs.existsSync(prodPath)) {
      return prodPath;
    }

    throw new Error('❌ 找不到 commands 目錄');
  }

  /**
   * 啟動 Python 伺服器
   */
  async start() {
    console.log('🚀 啟動 Python 伺服器...');
    console.log(`📂 Commands 路徑: ${this.commandsPath}`);

    try {
      // 啟動 HTTP Server
      await this.startHttpServer();

      // 啟動 WebSocket Server
      await this.startWebSocketServer();

      console.log('✅ Python 伺服器啟動完成');
      return true;
    } catch (error) {
      console.error('❌ Python 伺服器啟動失敗:', error);
      this.stop();
      throw error;
    }
  }

  /**
   * 啟動 HTTP Server
   */
  startHttpServer() {
    return new Promise((resolve, reject) => {
      console.log(`🌐 啟動 HTTP Server (port ${this.httpPort})...`);

      this.httpProcess = spawn('python3', [
        '-m', 'http.server',
        this.httpPort.toString()
      ], {
        cwd: this.commandsPath,
        stdio: ['ignore', 'pipe', 'pipe']
      });

      this.httpProcess.stdout.on('data', (data) => {
        console.log(`[HTTP] ${data.toString().trim()}`);
      });

      this.httpProcess.stderr.on('data', (data) => {
        const message = data.toString().trim();
        console.error(`[HTTP Error] ${message}`);

        // 檢查是否啟動成功
        if (message.includes('Serving HTTP')) {
          resolve();
        }
      });

      this.httpProcess.on('error', (error) => {
        console.error('❌ HTTP Server 錯誤:', error);
        reject(error);
      });

      this.httpProcess.on('exit', (code) => {
        if (code !== 0 && code !== null) {
          console.error(`❌ HTTP Server 異常退出 (code: ${code})`);
        }
      });

      // 等待 1 秒確認啟動
      setTimeout(() => {
        if (this.httpProcess && !this.httpProcess.killed) {
          console.log(`✅ HTTP Server 已啟動 (PID: ${this.httpProcess.pid})`);
          resolve();
        } else {
          reject(new Error('HTTP Server 啟動超時'));
        }
      }, 1000);
    });
  }

  /**
   * 啟動 WebSocket Server
   */
  startWebSocketServer() {
    return new Promise((resolve, reject) => {
      console.log(`📡 啟動 WebSocket Server (port ${this.wsPort})...`);

      const wsScript = path.join(this.commandsPath, 'websocket-server.py');

      if (!fs.existsSync(wsScript)) {
        reject(new Error(`找不到 websocket-server.py: ${wsScript}`));
        return;
      }

      this.wsProcess = spawn('python3', [
        wsScript,
        '--port', this.wsPort.toString()
      ], {
        cwd: this.commandsPath,
        stdio: ['ignore', 'pipe', 'pipe']
      });

      this.wsProcess.stdout.on('data', (data) => {
        const message = data.toString().trim();
        console.log(`[WS] ${message}`);

        // 檢查是否啟動成功
        if (message.includes('WebSocket Server') || message.includes('listening')) {
          resolve();
        }
      });

      this.wsProcess.stderr.on('data', (data) => {
        console.error(`[WS Error] ${data.toString().trim()}`);
      });

      this.wsProcess.on('error', (error) => {
        console.error('❌ WebSocket Server 錯誤:', error);
        reject(error);
      });

      this.wsProcess.on('exit', (code) => {
        if (code !== 0 && code !== null) {
          console.error(`❌ WebSocket Server 異常退出 (code: ${code})`);
        }
      });

      // 等待 2 秒確認啟動
      setTimeout(() => {
        if (this.wsProcess && !this.wsProcess.killed) {
          console.log(`✅ WebSocket Server 已啟動 (PID: ${this.wsProcess.pid})`);
          resolve();
        } else {
          reject(new Error('WebSocket Server 啟動超時'));
        }
      }, 2000);
    });
  }

  /**
   * 停止所有 Python 伺服器
   */
  stop() {
    console.log('🛑 停止 Python 伺服器...');

    if (this.httpProcess) {
      try {
        this.httpProcess.kill();
        console.log('✅ HTTP Server 已停止');
      } catch (error) {
        console.error('❌ 停止 HTTP Server 失敗:', error);
      }
      this.httpProcess = null;
    }

    if (this.wsProcess) {
      try {
        this.wsProcess.kill();
        console.log('✅ WebSocket Server 已停止');
      } catch (error) {
        console.error('❌ 停止 WebSocket Server 失敗:', error);
      }
      this.wsProcess = null;
    }
  }

  /**
   * 觸發掃描任務
   */
  async triggerScan() {
    console.log('🔍 觸發掃描任務...');
    // 透過 WebSocket 發送掃描指令
    // 實作方式：讓前端透過 WebSocket 發送，或直接執行 scan-real-data.py
    return new Promise((resolve, reject) => {
      const scanScript = path.join(this.commandsPath, 'scan-real-data.py');

      if (!fs.existsSync(scanScript)) {
        reject(new Error('找不到 scan-real-data.py'));
        return;
      }

      const scanProcess = spawn('python3', [scanScript], {
        cwd: this.commandsPath,
        stdio: 'inherit'
      });

      scanProcess.on('exit', (code) => {
        if (code === 0) {
          console.log('✅ 掃描完成');
          resolve();
        } else {
          reject(new Error(`掃描失敗 (code: ${code})`));
        }
      });

      scanProcess.on('error', (error) => {
        reject(error);
      });
    });
  }

  /**
   * 觸發健康檢查
   */
  async triggerHealthCheck() {
    console.log('🏥 觸發健康檢查...');
    return new Promise((resolve, reject) => {
      const healthScript = path.join(this.commandsPath, 'health-check.py');

      if (!fs.existsSync(healthScript)) {
        reject(new Error('找不到 health-check.py'));
        return;
      }

      const healthProcess = spawn('python3', [healthScript], {
        cwd: this.commandsPath,
        stdio: 'inherit'
      });

      healthProcess.on('exit', (code) => {
        if (code === 0) {
          console.log('✅ 健康檢查完成');
          resolve();
        } else {
          reject(new Error(`健康檢查失敗 (code: ${code})`));
        }
      });

      healthProcess.on('error', (error) => {
        reject(error);
      });
    });
  }
}

module.exports = PythonServerManager;
