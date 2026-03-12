const API = require('../../../utils/api.js');

Page({
  data: {
    breederId: null,
    breederName: '',
    sheepList: [],
    pagedSheepList: [],
    currentPage: 1,
    pageSize: 10,
    totalPages: 1,
    loading: false
  },

  onLoad(options) {
    const breederId = options.breeder_id;
    const breederName = decodeURIComponent(options.name || '');

    if (!breederId) {
      wx.showToast({ title: '参数缺失', icon: 'none' });
      return;
    }

    this.setData({
      breederId: breederId,
      breederName: breederName || '养殖户'
    });

    this.loadBreederSheep(breederId);
  },

  loadBreederSheep(breederId) {
    const token = wx.getStorageSync('token') || '';
    this.setData({ loading: true });

    API.request(`/api/breeders/${breederId}`, 'GET', { token: token })
      .then((res) => {
        const breeder = (res && res.code === 0 && res.data) ? res.data : res;
        const baseUrl = API.API_BASE_URL || '';

        let sheepList = (breeder && breeder.sheep_list && Array.isArray(breeder.sheep_list)) ? breeder.sheep_list : [];
        sheepList = sheepList.map(item => {
          let image = item.image_url || item.image || '';
          if (image && !image.startsWith('http://') && !image.startsWith('https://')) {
            image = baseUrl + image;
          }
          return {
            ...item,
            image_url: image
          };
        });

        this.setData({
          breederName: (breeder && breeder.name) || this.data.breederName,
          sheepList: sheepList,
          currentPage: 1,
          loading: false
        });

        this.updatePagedList();
      })
      .catch((err) => {
        console.error('加载养殖户羊只失败:', err);
        this.setData({ loading: false });
        wx.showToast({ title: '加载失败', icon: 'none' });
      });
  },

  updatePagedList() {
    const list = this.data.sheepList || [];
    const pageSize = this.data.pageSize || 10;
    const totalPages = Math.max(1, Math.ceil(list.length / pageSize));
    let currentPage = this.data.currentPage;

    if (currentPage > totalPages) currentPage = totalPages;
    if (currentPage < 1) currentPage = 1;

    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;

    this.setData({
      totalPages,
      currentPage,
      pagedSheepList: list.slice(start, end)
    });
  },

  goPrevPage() {
    if (this.data.currentPage <= 1) return;
    this.setData({ currentPage: this.data.currentPage - 1 });
    this.updatePagedList();
  },

  goNextPage() {
    if (this.data.currentPage >= this.data.totalPages) return;
    this.setData({ currentPage: this.data.currentPage + 1 });
    this.updatePagedList();
  },

  viewSheepDetail(e) {
    const sheepId = e.currentTarget.dataset.id;
    if (!sheepId) return;
    wx.navigateTo({
      url: `/pages/adopt/customize/customize?id=${sheepId}`
    });
  }
});
