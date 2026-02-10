const net = require('net');

/**
 * 檢查指定端口是否可用
 * @param {number} port - 要檢查的端口
 * @returns {Promise<boolean>} - 端口可用返回 true
 */
function isPortAvailable(port) {
  return new Promise((resolve) => {
    const server = net.createServer();

    server.once('error', (err) => {
      if (err.code === 'EADDRINUSE') {
        resolve(false);
      } else {
        resolve(false);
      }
    });

    server.once('listening', () => {
      server.close();
      resolve(true);
    });

    server.listen(port, '127.0.0.1');
  });
}

/**
 * 在指定範圍內尋找可用端口
 * @param {number} startPort - 起始端口
 * @param {number} endPort - 結束端口
 * @returns {Promise<number>} - 可用的端口號
 * @throws {Error} - 找不到可用端口時拋出錯誤
 */
async function findAvailablePort(startPort = 8891, endPort = 8999) {
  console.log(`🔍 搜尋可用端口 (${startPort}-${endPort})...`);

  for (let port = startPort; port <= endPort; port++) {
    const available = await isPortAvailable(port);
    if (available) {
      console.log(`✅ 找到可用端口: ${port}`);
      return port;
    }
  }

  throw new Error(`❌ 無法在 ${startPort}-${endPort} 範圍內找到可用端口`);
}

/**
 * 批次檢查多個端口
 * @param {number[]} ports - 要檢查的端口列表
 * @returns {Promise<Object>} - 端口可用性對照表
 */
async function checkPorts(ports) {
  const results = {};

  for (const port of ports) {
    results[port] = await isPortAvailable(port);
  }

  return results;
}

module.exports = {
  isPortAvailable,
  findAvailablePort,
  checkPorts
};
