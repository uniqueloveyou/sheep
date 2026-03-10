const monitorApi = require('./monitorApi.js')

Page({
  data: {
    loading: true,
    refreshing: false,
    token: '',
    breeders: [],
    filteredBreeders: [],
    keyword: ''
  },

  onShow() {
    this.bootstrap()
  },

  async onPullDownRefresh() {
    this.setData({ refreshing: true })
    await this.loadBreeders()
    this.setData({ refreshing: false })
    wx.stopPullDownRefresh()
  },

  async bootstrap() {
    const token = monitorApi.ensureLogin()
    if (!token) {
      this.setData({ loading: false })
      return
    }
    this.setData({ token })
    await this.loadBreeders()
  },

  async loadBreeders() {
    try {
      this.setData({ loading: true })
      const breeders = await monitorApi.fetchBreeders()
      const breederList = Array.isArray(breeders) ? breeders : []
      this.setData({
        breeders: breederList,
        filteredBreeders: this.filterBreeders(this.data.keyword, breederList),
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

  onKeywordInput(e) {
    const keyword = (e.detail.value || '').trim()
    const filteredBreeders = this.filterBreeders(keyword)
    this.setData({ keyword, filteredBreeders })
  },

  filterBreeders(keyword, source) {
    const query = (keyword || '').toLowerCase()
    const list = Array.isArray(source) ? source : this.data.breeders
    if (!query) return list
    return list.filter((item) => {
      const text = `${item.nickname || ''} ${item.username || ''} ${item.mobile || ''}`.toLowerCase()
      return text.includes(query)
    })
  },

  goToBreeder(e) {
    const breederId = e.currentTarget.dataset.id
    const breederName = e.currentTarget.dataset.name || ''
    if (!breederId) return

    wx.navigateTo({
      url: `/pages/monitor/devices/index?breederId=${breederId}&breederName=${encodeURIComponent(breederName)}`
    })
  }
})
