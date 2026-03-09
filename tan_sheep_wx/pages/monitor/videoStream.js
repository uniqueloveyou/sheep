/**
 * 视频流配置和管理工具
 */

// 视频流配置（可以从后端API获取）
// ⚠️ 重要提示：微信小程序要求使用HTTPS协议，HTTP协议在正式环境不支持
// 在开发者工具中，可以开启"不校验合法域名"来测试HTTP视频流
// 正式发布前，必须将视频流服务器配置为HTTPS
const VIDEO_STREAM_CONFIG = {
  monitor1: {
    id: 'monitor1',
    name: '一号监控',
    streamUrl: 'http://172.20.10.6:8080/live/01.m3u8', // ⚠️ 需要改为HTTPS
    streamType: 'hls', // hls, rtmp, http-flv, webrtc
    fallbackUrls: [
      'http://172.20.10.6:8080/live/01.flv', // ⚠️ 需要改为HTTPS
      'http://172.20.10.6:8080/live/01.mp4'  // ⚠️ 需要改为HTTPS
    ],
    enabled: true
  },
  monitor2: {
    id: 'monitor2',
    name: '二号监控',
    streamUrl: 'http://172.20.10.6:8080/live/02.m3u8', // ⚠️ 需要改为HTTPS
    streamType: 'hls',
    fallbackUrls: [
      'http://172.20.10.6:8080/live/02.flv', // ⚠️ 需要改为HTTPS
      'http://172.20.10.6:8080/live/02.mp4'  // ⚠️ 需要改为HTTPS
    ],
    enabled: true
  },
  monitor3: {
    id: 'monitor3',
    name: '三号监控',
    streamUrl: 'http://169.254.80.116:8080/live/03.m3u8', // ⚠️ 需要改为HTTPS
    streamType: 'hls',
    fallbackUrls: [
      'http://169.254.80.116:8080/live/03.flv', // ⚠️ 需要改为HTTPS
      'http://169.254.80.116:8080/live/03.mp4'  // ⚠️ 需要改为HTTPS
    ],
    enabled: true
  },
  monitor4: {
    id: 'monitor4',
    name: '四号监控',
    streamUrl: 'http://169.254.80.116:8080/live/04.m3u8', // ⚠️ 需要改为HTTPS
    streamType: 'hls',
    fallbackUrls: [
      'http://169.254.80.116:8080/live/04.flv', // ⚠️ 需要改为HTTPS
      'http://169.254.80.116:8080/live/04.mp4'  // ⚠️ 需要改为HTTPS
    ],
    enabled: true
  }
};

/**
 * 获取监控视频流配置
 * @param {string} monitorId 监控ID (monitor1, monitor2, etc.)
 * @returns {object} 视频流配置
 */
function getStreamConfig(monitorId) {
  return VIDEO_STREAM_CONFIG[monitorId] || null;
}

/**
 * 从后端API获取视频流地址（如果后端支持）
 * @param {string} monitorId 监控ID
 * @returns {Promise} 返回视频流配置
 */
function fetchStreamFromAPI(monitorId) {
  return new Promise((resolve, reject) => {
    // 如果后端有API，可以这样调用
    /*
    const API = require('./api.js');
    API.request('/api/monitor/stream', 'GET', { monitorId })
      .then(res => {
        if (res.code === 0 && res.data) {
          resolve(res.data);
        } else {
          // 如果API失败，使用本地配置
          resolve(getStreamConfig(monitorId));
        }
      })
      .catch(err => {
        console.error('获取视频流配置失败:', err);
        // API失败时使用本地配置
        resolve(getStreamConfig(monitorId));
      });
    */
    
    // 目前直接返回本地配置
    setTimeout(() => {
      resolve(getStreamConfig(monitorId));
    }, 100);
  });
}

/**
 * 检查视频流是否可用
 * @param {string} url 视频流地址
 * @returns {Promise<boolean>} 是否可用
 */
function checkStreamAvailable(url) {
  return new Promise((resolve) => {
    if (!url) {
      resolve(false);
      return;
    }
    
    // 微信小程序要求使用HTTPS协议
    if (url.startsWith('https://')) {
      // HTTPS协议，可以尝试访问
      resolve(true);
    } else if (url.startsWith('http://')) {
      // HTTP协议，在开发者工具中可能可以，但正式环境不支持
      // 提示用户需要HTTPS
      console.warn('警告：视频流使用HTTP协议，正式环境需要HTTPS');
      // 在开发者工具中可能可以，返回true
      resolve(true);
    } else {
      resolve(false);
    }
  });
}

/**
 * 获取视频流地址（支持fallback）
 * @param {string} monitorId 监控ID
 * @param {number} retryIndex 重试索引
 * @returns {Promise<string>} 可用的视频流地址
 */
async function getAvailableStreamUrl(monitorId, retryIndex = 0) {
  const config = await fetchStreamFromAPI(monitorId);
  if (!config || !config.enabled) {
    throw new Error('监控未启用或配置不存在');
  }
  
  const urls = [config.streamUrl, ...(config.fallbackUrls || [])];
  const url = urls[retryIndex];
  
  if (!url) {
    throw new Error('所有视频流地址都不可用');
  }
  
  const available = await checkStreamAvailable(url);
  if (available) {
    return url;
  } else if (retryIndex < urls.length - 1) {
    // 尝试下一个fallback地址
    return getAvailableStreamUrl(monitorId, retryIndex + 1);
  } else {
    throw new Error('视频流地址不可用');
  }
}

/**
 * 格式化视频流URL（处理相对路径等）
 * @param {string} url 原始URL
 * @returns {string} 格式化后的URL
 */
function formatStreamUrl(url) {
  if (!url) return '';
  
  // 如果是相对路径，转换为绝对路径
  if (url.startsWith('/')) {
    // 可以从配置中获取base URL
    const baseUrl = 'http://localhost:8080';
    return baseUrl + url;
  }
  
  return url;
}

module.exports = {
  getStreamConfig,
  fetchStreamFromAPI,
  checkStreamAvailable,
  getAvailableStreamUrl,
  formatStreamUrl,
  VIDEO_STREAM_CONFIG
};

