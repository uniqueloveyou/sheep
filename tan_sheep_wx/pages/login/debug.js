/**
 * 登录调试工具
 * 在登录页面添加调试按钮，用于测试登录功能
 */

// 在登录页面的onLoad中添加调试功能
function addDebugTools(page) {
  // 添加调试按钮到页面
  const debugInfo = {
    apiUrl: require('../../utils/api-config.js').getApiBaseUrl(),
    hasToken: !!wx.getStorageSync('token'),
    hasUid: !!wx.getStorageSync('uid')
  }
  
  console.log('=== 登录调试信息 ===')
  console.log('API地址:', debugInfo.apiUrl)
  console.log('已有Token:', debugInfo.hasToken)
  console.log('已有UID:', debugInfo.hasUid)
  console.log('==================')
  
  // 测试API连接
  page.testApiConnection = function() {
    console.log('测试API连接...')
    const API = require('../../utils/api.js')
    
    wx.request({
      url: API.API_BASE_URL + '/health',
      method: 'GET',
      success: function(res) {
        console.log('API连接成功:', res)
        wx.showModal({
          title: '连接成功',
          content: '后端服务正常运行\n\n响应: ' + JSON.stringify(res.data),
          showCancel: false
        })
      },
      fail: function(err) {
        console.error('API连接失败:', err)
        wx.showModal({
          title: '连接失败',
          content: '无法连接到后端服务器\n\n错误: ' + (err.errMsg || '未知错误') + '\n\n请检查：\n1. 后端服务是否启动\n2. API地址是否正确',
          showCancel: false
        })
      }
    })
  }
  
  // 测试获取code
  page.testGetCode = function() {
    console.log('测试获取微信code...')
    wx.login({
      success: function(res) {
        console.log('获取code成功:', res.code)
        wx.showModal({
          title: '获取成功',
          content: 'Code: ' + res.code.substring(0, 20) + '...',
          showCancel: false
        })
      },
      fail: function(err) {
        console.error('获取code失败:', err)
        wx.showModal({
          title: '获取失败',
          content: '错误: ' + (err.errMsg || '未知错误'),
          showCancel: false
        })
      }
    })
  }
}

module.exports = {
  addDebugTools
}

