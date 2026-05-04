const API = require('../../../utils/api.js');

const TRACE_SEEN_STORAGE_KEY = 'mySheepTraceSeenMap';
const TRACE_UNREAD_STORAGE_KEY = 'mySheepTraceUnreadCount';
const ACTIVE_ADOPTION_STATUSES = ['paid', 'adopting', 'ready_to_ship', 'settlement_pending', 'awaiting_delivery'];
const STATUS_LABELS = {
  paid: '认养中',
  adopting: '认养中',
  ready_to_ship: '认养中',
  settlement_pending: '认养中',
  awaiting_delivery: '待交付',
  shipping: '交付中',
  completed: '已完成',
  cancelled: '已取消',
  pending: '待支付'
};

function getTraceSeenMap() {
  return wx.getStorageSync(TRACE_SEEN_STORAGE_KEY) || {};
}

function saveTraceUnreadCount(count) {
  wx.setStorageSync(TRACE_UNREAD_STORAGE_KEY, count > 0 ? count : 0);
}

function hasNewTraceUpdate(sheepId, latestDate, seenMap) {
  if (!sheepId || !latestDate) {
    return false;
  }
  const seenDate = seenMap[String(sheepId)] || '';
  return !seenDate || latestDate > seenDate;
}

Page({
  data: {
    adoptingList: [],
    otherList: [],
    otherExpanded: false,
    loading: false,
    traceUnreadCount: 0
  },

  onShow() {
    this.loadMySheep();
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      const tabBar = this.getTabBar();
      tabBar.initTabBar();
      const index = tabBar.data.list.findIndex(item => item.pagePath === '/pages/my/adopt/adopt');
      if (index > -1) {
        tabBar.setData({ selected: index });
      }
    }
  },

  loadMySheep() {
    const token = wx.getStorageSync('token');
    if (!token) {
      saveTraceUnreadCount(0);
      this.setData({ adoptingList: [], otherList: [], traceUnreadCount: 0 });
      return;
    }

    this.setData({ loading: true });
    Promise.all([
      API.getMySheep(token),
      API.getMySheepUpdates(token).catch(() => ({ data: { updates: [] } }))
    ])
      .then(([res, updatesRes]) => {
        const items = Array.isArray(res.data || res) ? (res.data || res) : [];
        const baseUrl = API.API_BASE_URL;
        const seenMap = getTraceSeenMap();
        const traceUpdates = updatesRes && updatesRes.data && Array.isArray(updatesRes.data.updates)
          ? updatesRes.data.updates
          : [];
        const updateMap = {};
        let traceUnreadCount = 0;

        traceUpdates.forEach(item => {
          updateMap[String(item.sheep_id)] = item;
        });

        items.forEach(item => {
          if (item.sheep && item.sheep.image) {
            const imageUrl = item.sheep.image;
            item.sheep.image = imageUrl.startsWith('http://') || imageUrl.startsWith('https://')
              ? imageUrl
              : baseUrl + imageUrl;
          }

          const traceUpdate = updateMap[String(item.sheep && item.sheep.id)] || null;
          const latestTraceDate = traceUpdate && traceUpdate.latest_update_date
            ? traceUpdate.latest_update_date
            : '';
          const hasNewTrace = hasNewTraceUpdate(item.sheep && item.sheep.id, latestTraceDate, seenMap);

          item.traceUpdate = traceUpdate;
          item.latestTraceDate = latestTraceDate;
          item.hasNewTrace = hasNewTrace;
          item.traceHintText = hasNewTrace && traceUpdate
            ? `有新的${traceUpdate.latest_update_label || '溯源'}动态`
            : '';
          item.order_status = STATUS_LABELS[item.order_status_key] || item.order_status || item.order_status_key;
          item.canRequestEnd = ['paid', 'adopting', 'ready_to_ship'].includes(item.order_status_key);
          if (hasNewTrace) {
            traceUnreadCount += 1;
          }
        });

        const adoptingList = items.filter(item => ACTIVE_ADOPTION_STATUSES.includes(item.order_status_key));
        const otherList = items.filter(item => !ACTIVE_ADOPTION_STATUSES.includes(item.order_status_key));

        saveTraceUnreadCount(traceUnreadCount);
        this.setData({
          adoptingList,
          otherList,
          traceUnreadCount,
          loading: false
        });

        if (typeof this.getTabBar === 'function' && this.getTabBar()) {
          const tabBar = this.getTabBar();
          if (tabBar.refreshBadges) {
            tabBar.refreshBadges();
          } else {
            tabBar.initTabBar();
          }
        }
      })
      .catch(() => {
        this.setData({ loading: false });
        wx.showToast({ title: '获取数据失败', icon: 'none' });
      });
  },

  toggleOther() {
    this.setData({ otherExpanded: !this.data.otherExpanded });
  },

  viewSheepDetail(e) {
    const sheepId = e.currentTarget.dataset.sheepId;
    const latestTraceDate = e.currentTarget.dataset.latestTraceDate || '';
    const url = latestTraceDate
      ? `/packageUser/my/sheep-detail/index?id=${sheepId}&latest_trace_date=${encodeURIComponent(latestTraceDate)}`
      : `/packageUser/my/sheep-detail/index?id=${sheepId}`;
    wx.navigateTo({ url });
  },

  requestEndAdoption(e) {
    const orderId = e.currentTarget.dataset.orderId;
    const token = wx.getStorageSync('token');
    if (!token || !orderId) return;

    wx.showModal({
      title: '申请交付',
      content: '申请后订单进入待交付阶段，养殖户确认羊只具备交付条件后会补充物流信息。',
      success: async (res) => {
        if (!res.confirm) return;
        try {
          wx.showLoading({ title: '提交中...', mask: true });
          await API.requestEndAdoption(token, orderId);
          wx.hideLoading();
          wx.showToast({ title: '已申请交付', icon: 'success' });
          this.loadMySheep();
        } catch (err) {
          wx.hideLoading();
          wx.showToast({ title: err.message || '申请失败', icon: 'none' });
        }
      }
    });
  },

  goHome() {
    wx.switchTab({ url: '/pages/index/index' });
  }
});
