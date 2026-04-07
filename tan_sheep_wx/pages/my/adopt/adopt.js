// adopt.js - 我的羊页面
const API = require('../../../utils/api.js');

const TRACE_SEEN_STORAGE_KEY = 'mySheepTraceSeenMap';
const TRACE_UNREAD_STORAGE_KEY = 'mySheepTraceUnreadCount';

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

  onShow: function () {
    this.loadMySheep();
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      const tabBar = this.getTabBar();
      tabBar.initTabBar();
      const index = tabBar.data.list.findIndex(item => item.pagePath === "/pages/my/adopt/adopt");
      if (index > -1) {
        tabBar.setData({ selected: index });
      }
    }
  },

  loadMySheep: function () {
    const that = this;
    const token = wx.getStorageSync('token');
    if (!token) {
      saveTraceUnreadCount(0);
      that.setData({ adoptingList: [], otherList: [], traceUnreadCount: 0 });
      return;
    }
    that.setData({ loading: true });

    Promise.all([
      API.getMySheep(token),
      API.getMySheepUpdates(token).catch((error) => {
        console.warn('[我的羊] 获取溯源更新摘要失败:', error);
        return { data: { updates: [] } };
      })
    ])
      .then(([res, updatesRes]) => {
        const sheepData = res.data || res;
        const items = Array.isArray(sheepData) ? sheepData : [];
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
            const img = item.sheep.image;
            item.sheep.image = (img.startsWith('http://') || img.startsWith('https://'))
              ? img : baseUrl + img;
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

          if (hasNewTrace) {
            traceUnreadCount += 1;
          }
        });

        const adoptingList = items.filter(i => i.order_status_key === 'paid');
        const otherList = items.filter(i => i.order_status_key !== 'paid');

        saveTraceUnreadCount(traceUnreadCount);

        that.setData({
          adoptingList,
          otherList,
          traceUnreadCount,
          loading: false
        });

        if (typeof that.getTabBar === 'function' && that.getTabBar()) {
          const tabBar = that.getTabBar();
          if (tabBar.refreshBadges) {
            tabBar.refreshBadges();
          } else {
            tabBar.initTabBar();
          }
        }
      })
      .catch((error) => {
        console.error('[我的羊] 获取失败:', error);
        that.setData({ loading: false });
        wx.showToast({ title: '获取数据失败', icon: 'none' });
      });
  },

  toggleOther: function () {
    this.setData({ otherExpanded: !this.data.otherExpanded });
  },

  viewSheepDetail: function (e) {
    const sheepId = e.currentTarget.dataset.sheepId;
    const latestTraceDate = e.currentTarget.dataset.latestTraceDate || '';
    const url = latestTraceDate
      ? `/packageUser/my/sheep-detail/index?id=${sheepId}&latest_trace_date=${encodeURIComponent(latestTraceDate)}`
      : `/packageUser/my/sheep-detail/index?id=${sheepId}`;
    wx.navigateTo({ url });
  },

  goHome: function () {
    wx.switchTab({ url: '/pages/index/index' });
  }
});
