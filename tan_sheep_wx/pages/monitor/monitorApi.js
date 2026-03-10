const API = require('../../utils/api.js')

function ensureLogin() {
  const token = wx.getStorageSync('token') || ''
  if (token) {
    return token
  }

  wx.showModal({
    title: '提示',
    content: '请先登录',
    confirmText: '去登录',
    success(res) {
      if (res.confirm) {
        wx.navigateTo({
          url: '/pages/login/index'
        })
      }
    }
  })
  return ''
}

function ensureSuccess(res) {
  if (!res || res.code !== 0) {
    const msg = (res && res.msg) || '请求失败'
    throw new Error(msg)
  }
  return res.data
}

function normalizeDevice(device) {
  const online = device && device.status === 'online' && device.is_active !== false
  return {
    id: device.id,
    ownerId: device.owner_id,
    ownerName: device.owner_name || '',
    name: device.name || '未命名监控',
    deviceCode: device.device_code || '',
    streamUrl: device.stream_url || '',
    location: device.location || '未设置位置',
    status: online ? 'online' : 'offline',
    statusText: online ? '在线' : '离线',
    isActive: device.is_active !== false,
    updatedAt: device.updated_at || '',
    lastHeartbeat: device.last_heartbeat || ''
  }
}

function normalizeBreeder(item) {
  return {
    id: item.id,
    username: item.username || '',
    nickname: item.nickname || item.name || '',
    mobile: item.mobile || item.phone || '',
    monitor_count: item.monitor_count !== undefined ? item.monitor_count : '-',
    is_verified: item.is_verified !== false
  }
}

async function fetchBreeders() {
  const res = await API.request('/api/breeders', 'GET')
  const data = Array.isArray(res) ? res : ensureSuccess(res)
  return Array.isArray(data) ? data.map(normalizeBreeder) : []
}

async function fetchDevices(token, breederId) {
  const res = await API.getMonitorDevices(token, breederId)
  const data = ensureSuccess(res)
  return Array.isArray(data) ? data.map(normalizeDevice) : []
}

module.exports = {
  ensureLogin,
  fetchBreeders,
  fetchDevices,
  normalizeDevice,
  normalizeBreeder
}
