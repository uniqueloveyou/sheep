const API = require('../../../utils/api.js');

Page({
  data: {
    list: [],
    page: 1,
    pageSize: 10,
    loading: false,
    hasMore: true
  },

  onLoad() {
    this.fetchList(true);
  },

  onPullDownRefresh() {
    this.fetchList(true).finally(() => {
      wx.stopPullDownRefresh();
    });
  },

  onReachBottom() {
    if (this.data.loading || !this.data.hasMore) {
      return;
    }
    this.fetchList(false);
  },

  fetchList(reset) {
    const nextPage = reset ? 1 : this.data.page;
    this.setData({ loading: true });

    return API.getNewsList(nextPage, this.data.pageSize)
      .then((res) => {
        if (!res || res.code !== 0 || !res.data || !Array.isArray(res.data.list)) {
          throw new Error((res && res.msg) || '加载失败');
        }
        const incoming = res.data.list.map((item) => ({
          id: item.id,
          title: item.title,
          summary: item.summary || '',
          cover: item.cover || '',
          publishedAt: item.published_at || '',
          topSlot: item.top_slot
        }));

        this.setData({
          list: reset ? incoming : this.data.list.concat(incoming),
          page: (res.data.page || nextPage) + 1,
          hasMore: !!res.data.has_more,
          loading: false
        });
      })
      .catch((err) => {
        this.setData({ loading: false });
        wx.showToast({
          title: (err && err.message) || '加载失败',
          icon: 'none'
        });
      });
  },

  onTapItem(e) {
    const id = e.currentTarget.dataset.id;
    if (!id) return;
    wx.navigateTo({
      url: `/pages/news/detail/index?id=${id}`
    });
  }
});
