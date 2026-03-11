const API = require('../../../utils/api.js');

Page({
  data: {
    loading: true,
    news: {
      id: '',
      title: '',
      summary: '',
      cover: '',
      content: '',
      published_at: ''
    }
  },

  onLoad(options) {
    const id = options && options.id ? options.id : '';
    if (!id) {
      wx.showToast({
        title: '资讯ID无效',
        icon: 'none'
      });
      this.setData({ loading: false });
      return;
    }
    this.loadNewsDetail(id);
  },

  loadNewsDetail(newsId) {
    this.setData({ loading: true });
    API.getNewsDetail(newsId)
      .then((res) => {
        if (!res || res.code !== 0 || !res.data) {
          throw new Error((res && res.msg) || '资讯不存在');
        }
        this.setData({
          loading: false,
          news: res.data
        });
      })
      .catch((err) => {
        this.setData({ loading: false });
        wx.showToast({
          title: (err && err.message) || '加载失败',
          icon: 'none'
        });
      });
  }
});
