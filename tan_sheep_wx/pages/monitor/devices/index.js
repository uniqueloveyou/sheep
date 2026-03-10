const monitorApi = require('../monitorApi.js')

function formatTime(value) {
  if (!value) return '-'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '-'
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

Page({
  data: {
    loading: true,
    token: '',
    breederId: '',
    breederName: '',
    devices: [],
    onlineCount: 0
  },

  onLoad(options) {
    const breederId = options.breederId || ''
    const breederName = decodeURIComponent(options.breederName || '')
    this.setData({ breederId, breederName })
    if (breederName) {
      wx.setNavigationBarTitle({
        title: `${breederName}的监控`
      })
    }
  },

  onShow() {
    this.bootstrap()
  },

  async onPullDownRefresh() {
    await this.loadDevices()
    wx.stopPullDownRefresh()
  },

  async bootstrap() {
    const token = monitorApi.ensureLogin()
    if (!token) {
      this.setData({ loading: false })
      return
    }
    this.setData({ token })
    await this.loadDevices()
  },

  async loadDevices() {
    try {
      this.setData({ loading: true })
      const list = await monitorApi.fetchDevices(this.data.token, this.data.breederId)
      const devices = list.map((item) => ({
        ...item,
        updatedAtText: formatTime(item.updatedAt),
        heartbeatText: formatTime(item.lastHeartbeat)
      }))
      const onlineCount = devices.filter((d) => d.status === 'online').length
      this.setData({
        devices,
        onlineCount,
        loading: false
      })
    } catch (err) {
      this.setData({ loading: false })
      wx.showToast({
        title: err.message || '加载失败',
        icon: 'none'
      })
    }
  },

  goToPlayer(e) {
    const id = e.currentTarget.dataset.id
    const item = this.data.devices.find((d) => String(d.id) === String(id))
    if (!item) return

    wx.navigateTo({
      url: `/pages/monitor/player/index?device=${encodeURIComponent(JSON.stringify(item))}`
    })
  }
})
