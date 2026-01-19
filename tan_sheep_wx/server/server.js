/**
 * 本地图片服务器
 * 使用 Express 搭建静态文件服务器
 * 
 * 安装依赖：
 * npm install express cors
 * 
 * 启动服务器：
 * node server.js
 */

const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 5001;

// 允许跨域请求（微信小程序需要）
app.use(cors());

// 设置静态文件目录
// 假设图片文件放在 server/images/ 目录下
app.use('/images', express.static(path.join(__dirname, 'images')));

// 根路径提示
app.get('/', (req, res) => {
  const os = require('os');
  const networkInterfaces = os.networkInterfaces();
  let localIP = '未获取到';
  
  // 自动获取本机IP地址
  for (const interfaceName in networkInterfaces) {
    const interfaces = networkInterfaces[interfaceName];
    for (const iface of interfaces) {
      if (iface.family === 'IPv4' && !iface.internal) {
        localIP = iface.address;
        break;
      }
    }
    if (localIP !== '未获取到') break;
  }
  
  res.send(`
    <html>
    <head>
      <meta charset="UTF-8">
      <title>本地图片服务器</title>
      <style>
        body { font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }
        h1 { color: #238E23; }
        .info { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0; }
        code { background: #e8e8e8; padding: 2px 6px; border-radius: 3px; }
        ul { line-height: 1.8; }
      </style>
    </head>
    <body>
      <h1>🚀 本地图片服务器运行中</h1>
      <div class="info">
        <p><strong>端口：</strong>${PORT}</p>
        <p><strong>本地访问：</strong><code>http://localhost:${PORT}</code></p>
        <p><strong>局域网访问：</strong><code>http://${localIP}:${PORT}</code></p>
      </div>
      <h2>📦 图片访问地址示例：</h2>
      <ul>
        <li><code>http://localhost:${PORT}/images/banners/A.jpg</code></li>
        <li><code>http://localhost:${PORT}/images/recipe/01.jpg</code></li>
        <li><code>http://localhost:${PORT}/images/feed/xiaoyang.jpg</code></li>
      </ul>
      <h2>💡 提示：</h2>
      <ul>
        <li>将图片文件放到 <code>server/images/</code> 目录下</li>
        <li>保持原有的目录结构（如 05/, 08/ 等）</li>
        <li>访问路径：<code>http://localhost:${PORT}/images/目录/文件名</code></li>
        <li>微信小程序开发时，在工具中勾选"不校验合法域名"</li>
      </ul>
    </body>
    </html>
  `);
});

// 启动服务器
app.listen(PORT, '0.0.0.0', () => {
  const os = require('os');
  const networkInterfaces = os.networkInterfaces();
  let localIP = '未获取到';
  
  // 自动获取本机IP地址
  for (const interfaceName in networkInterfaces) {
    const interfaces = networkInterfaces[interfaceName];
    for (const iface of interfaces) {
      if (iface.family === 'IPv4' && !iface.internal) {
        localIP = iface.address;
        break;
      }
    }
    if (localIP !== '未获取到') break;
  }
  
  console.log(`\n${'='.repeat(50)}`);
  console.log(`🚀 图片服务器已启动！`);
  console.log(`${'='.repeat(50)}`);
  console.log(`📦 本地访问：http://localhost:${PORT}`);
  console.log(`📦 局域网访问：http://${localIP}:${PORT}`);
  console.log(`\n💡 提示：`);
  console.log(`   - 将图片文件放到 server/images/ 目录下`);
  console.log(`   - 图片访问路径：http://localhost:${PORT}/images/...`);
  console.log(`   - 在浏览器访问 http://localhost:${PORT} 查看详情`);
  console.log(`   - 按 Ctrl+C 停止服务器\n`);
});

