/**
 * API配置
 * 根据环境自动选择API地址
 */

// 开发环境：本地后端
// 生产环境：修改为实际的后端服务器地址
const API_CONFIG = {
  // 开发环境（本地开发）- Django后端
  development: 'http://127.0.0.1:8000',
  
  // 生产环境（部署后）- 请修改为实际的生产服务器地址
  production: 'http://127.0.0.1:8000',
  
  // 当前使用的环境（开发时使用development，部署时改为production）
  current: 'development'
}

// 获取当前API地址
function getApiBaseUrl() {
  return API_CONFIG[API_CONFIG.current] || API_CONFIG.development
}

module.exports = {
  API_CONFIG,
  getApiBaseUrl
}

