import { spawn } from 'child_process';
import path from 'path';
import { promises as fs } from 'fs';

let httpServerProcess = null;
let websocketServerProcess = null;

/**
 * 檢查 Python 環境與依賴
 */
export async function checkPythonEnv(resourcePath) {
  try {
    // 檢查 Python 版本
    const pythonVersion = await new Promise((resolve, reject) => {
      const proc = spawn('python3', ['--version']);
      let output = '';

      proc.stdout.on('data', (data) => {
        output += data.toString();
      });

      proc.stderr.on('data', (data) => {
        output += data.toString();
      });

      proc.on('close', (code) => {
        if (code === 0) {
          resolve(output.trim());
        } else {
          reject(new Error('Python not found'));
        }
      });
    });

    // 檢查 requirements.txt
    const requirementsPath = path.join(resourcePath, 'requirements.txt');
    const requirements = await fs.readFile(requirementsPath, 'utf-8');
    const dependencies = requirements
      .split('\n')
      .filter(line => line.trim() && !line.startsWith('#'))
      .map(line => line.trim());

    // 檢查依賴是否已安裝
    const missingDeps = [];
    for (const dep of dependencies) {
      const packageName = dep.split('==')[0].split('>=')[0].split('<=')[0];
      const isInstalled = await checkPythonPackage(packageName);
      if (!isInstalled) {
        missingDeps.push(packageName);
      }
    }

    if (missingDeps.length > 0) {
      return {
        success: false,
        error: `Missing Python packages: ${missingDeps.join(', ')}. Please run: pip3 install -r requirements.txt`
      };
    }

    return {
      success: true,
      version: pythonVersion,
      dependencies: dependencies.join(', ')
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * 檢查 Python 套件是否已安裝
 */
async function checkPythonPackage(packageName) {
  return new Promise((resolve) => {
    const proc = spawn('python3', ['-c', `import ${packageName.replace('-', '_')}`]);
    proc.on('close', (code) => {
      resolve(code === 0);
    });
  });
}

/**
 * 啟動所有後端服務
 */
export async function startAll(resourcePath) {
  console.log('[ProcessManager] Starting all services...');
  console.log('[ProcessManager] Resource path:', resourcePath);

  // 啟動 HTTP Server
  const httpServerScript = path.join(resourcePath, 'api-server.py');
  httpServerProcess = spawn('python3', [httpServerScript], {
    cwd: resourcePath,
    env: { ...process.env }
  });

  httpServerProcess.stdout.on('data', (data) => {
    console.log('[HTTP Server]', data.toString().trim());
  });

  httpServerProcess.stderr.on('data', (data) => {
    console.error('[HTTP Server Error]', data.toString().trim());
  });

  httpServerProcess.on('close', (code) => {
    console.log('[HTTP Server] Exited with code:', code);
  });

  // 啟動 WebSocket Server
  const websocketServerScript = path.join(resourcePath, 'websocket-server.py');
  websocketServerProcess = spawn('python3', [websocketServerScript], {
    cwd: resourcePath,
    env: { ...process.env }
  });

  websocketServerProcess.stdout.on('data', (data) => {
    console.log('[WebSocket Server]', data.toString().trim());
  });

  websocketServerProcess.stderr.on('data', (data) => {
    console.error('[WebSocket Server Error]', data.toString().trim());
  });

  websocketServerProcess.on('close', (code) => {
    console.log('[WebSocket Server] Exited with code:', code);
  });

  console.log('[ProcessManager] All services started');
  console.log('[ProcessManager] HTTP Server PID:', httpServerProcess.pid);
  console.log('[ProcessManager] WebSocket Server PID:', websocketServerProcess.pid);

  // 等待服務啟動
  await new Promise(resolve => setTimeout(resolve, 1500));
}

/**
 * 停止所有後端服務
 */
export async function stopAll() {
  console.log('[ProcessManager] Stopping all services...');

  if (httpServerProcess) {
    httpServerProcess.kill('SIGTERM');
    httpServerProcess = null;
  }

  if (websocketServerProcess) {
    websocketServerProcess.kill('SIGTERM');
    websocketServerProcess = null;
  }

  console.log('[ProcessManager] All services stopped');
}
