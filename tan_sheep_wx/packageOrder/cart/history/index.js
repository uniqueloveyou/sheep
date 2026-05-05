const API = require('../../../utils/api.js');

const STATUS_LABELS = {
  pending: '待支付',
  paid: '认养中',
  adopting: '认养中',
  ready_to_ship: '认养中',
  settlement_pending: '待结算',
  awaiting_delivery: '待交付',
  shipping: '交付中',
  completed: '已完成',
  cancelled: '已取消'
};

function formatAmount(value) {
  const amount = Number(value || 0);
  if (!Number.isFinite(amount)) return '0.00';
  return amount.toFixed(2).replace(/\.00$/, '');
}

function normalizeOrder(order) {
  const items = (order.items || []).map((item) => {
    const price = Number(item.price || 0);
    return Object.assign({}, item, {
      priceText: price > 0 ? `¥${formatAmount(price)}` : '已包含在认养费用中'
    });
  });

  return Object.assign({}, order, {
    items,
    status_display: STATUS_LABELS[order.status] || order.status_display || order.status,
    totalAmountText: formatAmount(order.total_amount)
  });
}

Page({
  data: {
    orders: [],
    loading: false
  },

  onLoad() {
    this.loadHistory();
  },

  onShow() {
    this.loadHistory();
  },

  loadHistory() {
    const token = wx.getStorageSync('token');
    if (!token) {
      wx.showModal({
        title: '提示',
        content: '请先登录查看认养记录',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({ url: '/pages/login/index' });
          } else {
            wx.navigateBack();
          }
        }
      });
      return;
    }

    this.setData({ loading: true });
    API.getOrderHistory(token)
      .then((res) => {
        const rawOrders = Array.isArray(res.data || res) ? (res.data || res) : [];
        const orders = rawOrders.map(normalizeOrder);
        this.setData({ orders, loading: false });
      })
      .catch(() => {
        this.setData({ loading: false });
        wx.showToast({ title: '获取认养记录失败', icon: 'none' });
      });
  },

  onOrderTap(e) {
    const order = e.currentTarget.dataset.order;
    if (!order || !order.id) {
      wx.showToast({ title: '认养数据异常', icon: 'none' });
      return;
    }

    wx.setStorageSync('currentOrderDetail', order);
    wx.navigateTo({
      url: `/packageOrder/cart/history/detail/index?order_id=${order.id}`
    });
  }
});
