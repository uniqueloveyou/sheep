const monitorApi = require('../monitorApi.js')

function safeParseDevice(str) {
  if (!str) return null
  try {
    return JSON.parse(decodeURIComponent(str))
  } catch (e) {
    return null
  }
}

Page({
  data: {
    token: '',
    device: null,
    isOnline: false,
    canPlay: false,
    loading: false,
    errorMessage: ''
  },

  onLoad(options) {
    const device = safeParseDevice(options.device)
    if (!device) {
      wx.showToast({
        title: '监控信息无效',
        icon: 'none'
      })
      setTimeout(() => wx.navigateBack(), 500)
      return
    }

    wx.setNavigationBarTitle({
      title: device.name || '监控画面'
    })

    const isOnline = device.status === 'online' && !!device.streamUrl
    this.setData({
      device,
      isOnline,
      canPlay: false,
      errorMessage: isOnline ? '' : '设备离线，暂不可播放'
    })
  },

  onShow() {
    const token = monitorApi.ensureLogin()
    if (!token) return
    this.setData({ token })
    if (this.data.isOnline) {
      // 延迟初始化，避免页面刚打开就占用大量资源导致卡顿
      this.tryPlay(250)
    }
  },

  onHide() {
    this.stopPlay()
  },

  onUnload() {
    this.stopPlay()
  },

  tryPlay(delay = 0) {
    clearTimeout(this.playTimer)
    this.playTimer = setTimeout(() => {
      this.setData({
        canPlay: true,
        loading: true,
        errorMessage: ''
      })
    }, delay)
  },

  stopPlay() {
    clearTimeout(this.playTimer)
    const ctx = wx.createVideoContext('monitor-video', this)
    if (ctx && ctx.stop) {
      ctx.stop()
    }
    this.setData({
      canPlay: false,
      loading: false
    })
  },

  onManualRetry() {
    if (!this.data.isOnline) return
    this.tryPlay(100)
  },

  onVideoPlay() {
    this.setData({
      loading: false,
      errorMessage: ''
    })
  },

  onVideoWaiting() {
    this.setData({
      loading: true
    })
  },

  onVideoLoaded() {
    this.setData({
      loading: false
    })
  },

  onVideoError() {
    this.setData({
      loading: false,
      canPlay: false,
      errorMessage: '视频流加载失败，请稍后重试'
    })
  }
})
