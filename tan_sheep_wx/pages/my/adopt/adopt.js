const API = require('../../../utils/api.js');

const TRACE_SEEN_STORAGE_KEY = 'mySheepTraceSeenMap';
const TRACE_UNREAD_STORAGE_KEY = 'mySheepTraceUnreadCount';
const ACTIVE_ADOPTION_STATUSES = ['paid', 'adopting', 'ready_to_ship', 'settlement_pending', 'awaiting_delivery'];
const STATUS_LABELS = {
  paid: '认养中',
  adopting: '认养中',
  ready_to_ship: '认养中',
  settlement_pending: '待结算',
  awaiting_delivery: '待交付',
  shipping: '交付中',
  completed: '已完成',
  cancelled: '已取消',
  pending: '待支付'
};
const TRACE_LABELS = {
  feeding: '喂养记录',
  Feeding: '喂养记录',
  growth: '生长记录',
  Growth: '生长记录',
  vaccination: '疫苗记录',
  Vaccination: '疫苗记录'
};
const CAN_REQUEST_END_STATUSES = ['paid', 'adopting', 'ready_to_ship'];

function formatAmount(value) {
  const amount = Number(value || 0);
  if (!Number.isFinite(amount)) {
    return '0.00';
  }
  return amount.toFixed(2).replace(/\.00$/, '');
}

function buildAssetUrl(url) {
  if (!url) {
    return '';
  }
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }
  return API.API_BASE_URL + url;
}

function getStatusClass(status) {
  if (status === 'settlement_pending') return 'status-settlement';
  if (status === 'awaiting_delivery') return 'status-awaiting';
  if (status === 'shipping') return 'status-shipping';
  if (status === 'completed') return 'status-completed';
  if (status === 'cancelled') return 'status-cancelled';
  return 'status-adopting';
}

function getOrderStatusText(item) {
  if (item.order_status_key === 'shipping') {
    return item.delivery_method === 'logistics' ? '已发货' : '交付中';
  }
  return STATUS_LABELS[item.order_status_key] || item.order_status || item.order_status_key;
}

function getTraceLabel(traceUpdate) {
  if (!traceUpdate) {
    return '';
  }
  return TRACE_LABELS[traceUpdate.latest_update_type]
    || TRACE_LABELS[traceUpdate.latest_update_label]
    || traceUpdate.latest_update_label
    || '溯源记录';
}

function getCareSummary(item) {
  const status = item.order_status_key;
  const days = Number(item.adoption_days || 0);
  const dailyFeeText = formatAmount(item.daily_care_fee);

  if (CAN_REQUEST_END_STATUSES.includes(status)) {
    return `已认养 ${days || 1} 天，基础照料费申请交付时结算`;
  }
  if (status === 'settlement_pending') {
    return `待支付基础照料费 ¥${formatAmount(item.care_fee_amount)}`;
  }
  if (status === 'awaiting_delivery') {
    return '服务费已结算，等待养殖户安排交付';
  }
  if (status === 'shipping') {
    return item.delivery_method === 'logistics'
      ? '养殖户已发货，可在认养记录中查看物流信息'
      : '养殖户已安排线下交付，请留意交付信息';
  }
  if (status === 'completed') {
    return '认养交付已完成';
  }
  return `基础照料费 ¥${dailyFeeText}/天`;
}

function getActionMeta(status) {
  if (CAN_REQUEST_END_STATUSES.includes(status)) {
    return { text: '申请交付', type: 'request', disabled: false };
  }
  if (status === 'settlement_pending') {
    return { text: '支付服务费', type: 'pay', disabled: false };
  }
  if (status === 'awaiting_delivery') {
    return { text: '等待交付', type: 'none', disabled: true };
  }
  if (status === 'shipping') {
    return { text: '查看详情', type: 'detail', disabled: false };
  }
  return { text: '查看详情', type: 'detail', disabled: false };
}

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
    traceUnreadCount: 0,
    showDeliveryModal: false,
    deliverySubmitting: false,
    deliveryForm: {
      orderId: null,
      adoptionDays: 1,
      dailyFeeText: '0.00',
      estimatedFeeText: '0.00',
      receiverName: '',
      receiverPhone: '',
      region: [],
      detailAddress: ''
    }
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
          if (!item.sheep) {
            item.sheep = {};
          }
          item.sheep.image = buildAssetUrl(item.sheep.image);

          const traceUpdate = updateMap[String(item.sheep && item.sheep.id)] || null;
          const latestTraceDate = traceUpdate && traceUpdate.latest_update_date
            ? traceUpdate.latest_update_date
            : '';
          const hasNewTrace = hasNewTraceUpdate(item.sheep && item.sheep.id, latestTraceDate, seenMap);
          const traceLabel = getTraceLabel(traceUpdate);
          const actionMeta = getActionMeta(item.order_status_key);

          item.traceUpdate = traceUpdate;
          item.latestTraceDate = latestTraceDate;
          item.hasNewTrace = hasNewTrace;
          item.traceHintText = hasNewTrace && traceUpdate
            ? `有新的${traceLabel}动态`
            : '';
          item.order_status = getOrderStatusText(item);
          item.statusClass = getStatusClass(item.order_status_key);
          item.traceSummaryText = traceUpdate && latestTraceDate
            ? `最新${traceLabel} · ${latestTraceDate}`
            : '暂无新的溯源动态';
          item.identityText = [
            item.sheep.gender,
            item.sheep.weight ? `${item.sheep.weight} kg` : '',
            item.sheep.age_display || ''
          ].filter(Boolean).join(' · ');
          item.careSummaryText = getCareSummary(item);
          item.actionText = actionMeta.text;
          item.actionType = actionMeta.type;
          item.actionDisabled = actionMeta.disabled;
          item.dailyCareFeeText = formatAmount(item.daily_care_fee);
          item.estimatedCareFeeText = formatAmount(item.estimated_care_fee);
          item.careFeeAmountText = formatAmount(item.care_fee_amount);
          item.canRequestEnd = actionMeta.type === 'request';
          item.canPayCareFee = actionMeta.type === 'pay';
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

  viewAdoptionEntry(e) {
    const recordId = Number(e.currentTarget.dataset.recordId);
    const items = (this.data.adoptingList || []).concat(this.data.otherList || []);
    const item = items.find(record => Number(record.id) === recordId);
    if (!item) {
      wx.showToast({ title: '认养信息不存在', icon: 'none' });
      return;
    }

    const latestTraceDate = item.latestTraceDate || '';
    const url = latestTraceDate
      ? `/packageUser/my/sheep-detail/index?id=${item.sheep.id}&latest_trace_date=${encodeURIComponent(latestTraceDate)}`
      : `/packageUser/my/sheep-detail/index?id=${item.sheep.id}`;
    wx.navigateTo({ url });
  },

  requestEndAdoption(e) {
    const orderId = e.currentTarget.dataset.orderId;
    const adoptionDays = e.currentTarget.dataset.adoptionDays || 1;
    const dailyFeeText = e.currentTarget.dataset.dailyFeeText || '0.00';
    const estimatedFeeText = e.currentTarget.dataset.estimatedFeeText || '0.00';
    if (!orderId) return;

    const lastAddress = wx.getStorageSync('lastShippingInfo') || {};
    this.setData({
      showDeliveryModal: true,
      deliverySubmitting: false,
      deliveryForm: {
        orderId,
        adoptionDays,
        dailyFeeText,
        estimatedFeeText,
        receiverName: lastAddress.receiverName || '',
        receiverPhone: lastAddress.receiverPhone || '',
        region: [],
        detailAddress: ''
      }
    });
  },

  closeDeliveryModal() {
    if (this.data.deliverySubmitting) return;
    this.setData({ showDeliveryModal: false });
  },

  stopModalTap() {},

  onDeliveryNameInput(e) {
    this.setData({ 'deliveryForm.receiverName': e.detail.value });
  },

  onDeliveryPhoneInput(e) {
    this.setData({ 'deliveryForm.receiverPhone': e.detail.value });
  },

  onDeliveryRegionChange(e) {
    this.setData({ 'deliveryForm.region': e.detail.value || [] });
  },

  onDeliveryAddressInput(e) {
    this.setData({ 'deliveryForm.detailAddress': e.detail.value });
  },

  async submitDeliveryApplication() {
    const form = this.data.deliveryForm || {};
    const token = wx.getStorageSync('token');
    const receiverName = String(form.receiverName || '').trim();
    const receiverPhone = String(form.receiverPhone || '').trim();
    const region = form.region || [];
    const detailAddress = String(form.detailAddress || '').trim();

    if (!token || !form.orderId) return;
    if (!receiverName) {
      wx.showToast({ title: '请填写收货人姓名', icon: 'none' });
      return;
    }
    if (!/^1\d{10}$/.test(receiverPhone)) {
      wx.showToast({ title: '请填写正确手机号', icon: 'none' });
      return;
    }
    if (!region.length) {
      wx.showToast({ title: '请选择省市区', icon: 'none' });
      return;
    }
    if (!detailAddress) {
      wx.showToast({ title: '请填写详细地址', icon: 'none' });
      return;
    }

    const shippingAddress = `${region.join(' ')} ${detailAddress}`;
    this.setData({ deliverySubmitting: true });
    try {
      await API.requestEndAdoption(token, form.orderId, {
        receiver_name: receiverName,
        receiver_phone: receiverPhone,
        shipping_address: shippingAddress
      });
      wx.setStorageSync('lastShippingInfo', {
        receiverName,
        receiverPhone,
        shippingAddress
      });
      this.setData({ showDeliveryModal: false, deliverySubmitting: false });
      wx.showToast({ title: '待支付服务费', icon: 'success' });
      this.loadMySheep();
    } catch (err) {
      this.setData({ deliverySubmitting: false });
      wx.showToast({ title: err.message || '申请失败', icon: 'none' });
    }
  },

  payCareFee(e) {
    const orderId = e.currentTarget.dataset.orderId;
    const careFeeText = e.currentTarget.dataset.careFeeText || '0.00';
    const token = wx.getStorageSync('token');
    if (!token || !orderId) return;

    wx.showModal({
      title: '支付服务费',
      content: `本次需支付基础照料服务费 ¥${careFeeText}。支付完成后，订单将进入待交付，由养殖户安排交付。`,
      success: async (res) => {
        if (!res.confirm) return;
        try {
          wx.showLoading({ title: '支付中...', mask: true });
          await API.payCareFee(token, orderId);
          wx.hideLoading();
          wx.showToast({ title: '支付成功', icon: 'success' });
          this.loadMySheep();
        } catch (err) {
          wx.hideLoading();
          wx.showToast({ title: err.message || '支付失败', icon: 'none' });
        }
      }
    });
  },

  goHome() {
    wx.switchTab({ url: '/pages/index/index' });
  }
});
