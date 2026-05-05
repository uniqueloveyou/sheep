const API = require('../../../utils/api.js');

const STATUS_TEXT_MAP = {
  available: '立即认养',
  in_my_cart: '去购物车支付',
  reserved_by_others: '暂时被锁定',
  adopted_by_me: '我已认养',
  adopted_by_others: '已被认养'
};

Page({
  data: {
    sheepId: null,
    sheepDetail: {},
    imagePath: '/images/icons/function/f1.png',
    growthRecords: [],
    vaccineRecords: [],
    adoptStatus: 'available',
    adoptStatusText: STATUS_TEXT_MAP.available
  },

  onLoad(options) {
    if (!options.id) {
      return;
    }
    const sheepId = options.id;
    this.setData({ sheepId });
    this.getSheepDetail(sheepId);
    this.fetchGrowthRecords(sheepId);
    this.fetchVaccineRecords(sheepId);
    this.checkAdoptStatus(sheepId);
  },

  checkAdoptStatus(sheepId) {
    const token = wx.getStorageSync('token') || '';
    API.request(`/api/sheep/${sheepId}/status?token=${token}`, 'GET')
      .then((res) => {
        if (res.code !== 0 || !res.data) {
          return;
        }
        const status = res.data.status || 'available';
        this.setData({
          adoptStatus: status,
          adoptStatusText: STATUS_TEXT_MAP[status] || res.data.status_text || STATUS_TEXT_MAP.available
        });
      })
      .catch(() => {
        this.setData({ adoptStatus: 'available', adoptStatusText: STATUS_TEXT_MAP.available });
      });
  },

  adoptSheep() {
    if (this.data.adoptStatus === 'in_my_cart') {
      wx.switchTab({ url: '/pages/cart/index' });
      return;
    }
    if (this.data.adoptStatus !== 'available') {
      return;
    }

    const token = wx.getStorageSync('token');
    if (!token) {
      wx.showModal({
        title: '提示',
        content: '请先登录后再认养',
        confirmText: '去登录',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({ url: '/pages/login/index' });
          }
        }
      });
      return;
    }

    const sheepId = this.data.sheepId || this.data.sheepDetail.id;
    if (!sheepId) {
      wx.showToast({ title: '羊只信息不完整', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '处理中...', mask: true });
    API.addToCart(token, sheepId, 1, this.data.sheepDetail.price || 0)
      .then((res) => {
        wx.hideLoading();
        if (res.code !== 0) {
          wx.showToast({ title: res.msg || '认养失败', icon: 'none' });
          return;
        }

        this.setData({
          adoptStatus: 'in_my_cart',
          adoptStatusText: STATUS_TEXT_MAP.in_my_cart
        });
        wx.showModal({
          title: '已加入购物车',
          content: '该羊只已加入购物车。完成支付后，系统会正式建立认养关系，并在认养期间持续展示溯源信息。',
          confirmText: '去购物车',
          cancelText: '稍后再说',
          success: (modalRes) => {
            if (modalRes.confirm) {
              wx.switchTab({ url: '/pages/cart/index' });
            }
          }
        });
      })
      .catch((err) => {
        wx.hideLoading();
        wx.showToast({ title: err.message || '网络错误，请重试', icon: 'none' });
      });
  },

  getSheepDetail(sheepId) {
    API.request(`/api/sheep/${sheepId}`, 'GET')
      .then((res) => {
        if (!res || typeof res !== 'object') {
          return;
        }
        const rawDailyCareFee = parseFloat(res.daily_care_fee);
        const sheepDetail = {
          id: res.id || sheepId,
          ear_tag: res.ear_tag || '',
          gender: res.gender || '未知',
          weight: res.weight ? parseFloat(res.weight).toFixed(1) : '0',
          height: res.height ? parseFloat(res.height).toFixed(1) : '0',
          length: res.length ? parseFloat(res.length).toFixed(1) : '0',
          birth_date: res.birth_date || '',
          age_display: res.age_display || '未设置',
          price: res.price ? parseFloat(res.price).toFixed(2) : '0.00',
          daily_care_fee: isNaN(rawDailyCareFee) ? '10.00' : rawDailyCareFee.toFixed(2),
          farm_name: res.farm_name || '宁夏盐池滩羊核心产区',
          breeder_name: res.breeder_name || '官方牧场',
          image: res.image || ''
        };
        if (sheepDetail.image && !sheepDetail.image.startsWith('http://') && !sheepDetail.image.startsWith('https://')) {
          sheepDetail.image = API.API_BASE_URL + sheepDetail.image;
        }
        this.setData({
          sheepDetail,
          imagePath: sheepDetail.image || this.data.imagePath
        });
      })
      .catch(() => {
        wx.showToast({ title: '羊只信息获取失败', icon: 'none', duration: 2000 });
      });
  },

  fetchGrowthRecords(sheepId) {
    API.request(`/api/growth/sheep/${sheepId}`, 'GET')
      .then((res) => {
        this.setData({ growthRecords: (res && res.growth_records) ? res.growth_records : [] });
      })
      .catch(() => {});
  },

  fetchVaccineRecords(sheepId) {
    API.request(`/vaccine_records/${sheepId}`, 'GET')
      .then((res) => {
        const formattedRecords = (res || []).map(record => ({
          ...record,
          VaccinationDate: this.formatDate(record.VaccinationDate),
          ExpiryDate: this.formatDate(record.ExpiryDate)
        }));
        this.setData({ vaccineRecords: formattedRecords });
      })
      .catch(() => {});
  },

  formatDate(dateString) {
    const date = new Date(dateString);
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
  },

  onImageError() {
    this.setData({ imagePath: '/images/icons/function/f1.png' });
  }
});
