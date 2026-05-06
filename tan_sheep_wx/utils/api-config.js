/**
 * API config
 *
 * In WeChat DevTools on Windows, localhost/127.0.0.1 usually points to the
 * same machine and is convenient for local Django debugging.
 * On a real phone, those addresses point to the phone itself, so we also keep
 * LAN candidates and remember the last reachable address automatically.
 */

const STORAGE_KEY = 'api_base_url'
const LAST_KNOWN_GOOD_KEY = 'api_base_url_last_known_good'

const API_CONFIG = {
  developmentCandidates: [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://sheep.youzilite.app'
  ],
  // 生产环境：Cloudflare Tunnel 域名
  production: 'https://sheep.youzilite.app',
  current: 'development'  // 开发/答辩演示默认走本地 Django，避免生产隧道 502 影响调试
}

function normalizeBaseUrl(url) {
  return String(url || '').trim().replace(/\/+$/, '')
}

function getStorageValue(key) {
  if (typeof wx === 'undefined' || typeof wx.getStorageSync !== 'function') {
    return ''
  }

  try {
    return normalizeBaseUrl(wx.getStorageSync(key))
  } catch (error) {
    console.warn(`[API config] failed to read ${key}`, error)
    return ''
  }
}

function getStoredApiBaseUrl() {
  return getStorageValue(STORAGE_KEY)
}

function getLastKnownGoodApiBaseUrl() {
  return getStorageValue(LAST_KNOWN_GOOD_KEY)
}

function getApiBaseUrlCandidates() {
  const currentConfig = API_CONFIG.current === 'development'
    ? (API_CONFIG.developmentCandidates || [])
    : [API_CONFIG[API_CONFIG.current] || API_CONFIG.production]

  const candidates = []
  const orderedUrls = API_CONFIG.current === 'development'
    ? currentConfig.concat([getStoredApiBaseUrl(), getLastKnownGoodApiBaseUrl()])
    : [getStoredApiBaseUrl(), getLastKnownGoodApiBaseUrl()].concat(currentConfig)

  orderedUrls.forEach((url) => {
    const normalizedUrl = normalizeBaseUrl(url)
    if (normalizedUrl && candidates.indexOf(normalizedUrl) === -1) {
      candidates.push(normalizedUrl)
    }
  })

  return candidates
}

function getDefaultApiBaseUrl() {
  return getApiBaseUrlCandidates()[0] || ''
}

function getApiBaseUrl() {
  return getDefaultApiBaseUrl()
}

function setApiBaseUrl(url) {
  const normalizedUrl = normalizeBaseUrl(url)
  if (!normalizedUrl) {
    throw new Error('API base URL cannot be empty')
  }

  wx.setStorageSync(STORAGE_KEY, normalizedUrl)
  return normalizedUrl
}

function rememberApiBaseUrl(url) {
  const normalizedUrl = normalizeBaseUrl(url)
  if (!normalizedUrl || typeof wx === 'undefined' || typeof wx.setStorageSync !== 'function') {
    return normalizedUrl
  }

  try {
    wx.setStorageSync(LAST_KNOWN_GOOD_KEY, normalizedUrl)
  } catch (error) {
    console.warn('[API config] failed to store last known good api_base_url', error)
  }

  return normalizedUrl
}

function clearApiBaseUrl() {
  if (typeof wx === 'undefined' || typeof wx.removeStorageSync !== 'function') {
    return
  }

  wx.removeStorageSync(STORAGE_KEY)
  wx.removeStorageSync(LAST_KNOWN_GOOD_KEY)
}

module.exports = {
  API_CONFIG,
  STORAGE_KEY,
  LAST_KNOWN_GOOD_KEY,
  normalizeBaseUrl,
  getDefaultApiBaseUrl,
  getApiBaseUrl,
  getApiBaseUrlCandidates,
  getLastKnownGoodApiBaseUrl,
  rememberApiBaseUrl,
  setApiBaseUrl,
  clearApiBaseUrl
}
