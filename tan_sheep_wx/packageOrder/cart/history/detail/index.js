function formatAmount(value) {
  const amount = Number(value || 0);
  if (!Number.isFinite(amount)) return '0.00';
  return amount.toFixed(2).replace(/\.00$/, '');
}

function getDisplayStatus(status) {
  const map = {
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
  return map[status] || '认养中';
}

function getStatusClass(status) {
  if (status === 'pending') return 'status-pending';
  if (status === 'settlement_pending') return 'status-settlement';
  if (status === 'awaiting_delivery') return 'status-awaiting';
  if (status === 'shipping') return 'status-shipping';
  if (status === 'completed') return 'status-completed';
  if (status === 'cancelled') return 'status-cancelled';
  return 'status-adopting';
}

function normalizeItem(item) {
  const price = Number(item.price || 0);
  return Object.assign({}, item, {
    weightText: item.weight ? `${item.weight} kg` : '未记录',
    healthStatus: item.health_status || item.healthStatus || '健康',
    priceText: price > 0 ? `¥${formatAmount(price)}` : '已包含在认养费用中'
  });
}

function normalizeOrder(order) {
  const items = (order.items || []).map(normalizeItem);
  const shippingAddress = order.shipping_address || '';
  const hasLogistics = !!(order.logistics_company || order.logistics_tracking_number || order.shipping_date);
  const isCompleted = order.status === 'completed';
  const isShipping = order.status === 'shipping';

  let deliveryStatusText = '暂未交付';
  let deliveryHint = '待羊只具备交付条件后，由养殖户安排交付。';
  if (isShipping) {
    deliveryStatusText = '交付中';
    deliveryHint = '';
  } else if (isCompleted) {
    deliveryStatusText = '已完成';
    deliveryHint = '';
  }

  return Object.assign({}, order, {
    items,
    status_display: getDisplayStatus(order.status),
    statusClass: getStatusClass(order.status),
    totalAmountText: formatAmount(order.total_amount),
    receiverNameText: order.receiver_name || '未填写',
    receiverPhoneText: order.receiver_phone || '未填写',
    shippingAddressText: shippingAddress || '可后续补充',
    primarySheepId: items[0] && items[0].sheep_id,
    hasLogistics,
    isCompleted,
    deliveryStatusText,
    deliveryHint
  });
}

Page({
  data: {
    order: null,
    orderId: null
  },

  onLoad(options) {
    const orderId = options.order_id ? Number(options.order_id) : null;
    const cached = wx.getStorageSync('currentOrderDetail');

    if (!cached || !cached.id) {
      wx.showToast({ title: '认养信息不存在', icon: 'none' });
      setTimeout(() => wx.navigateBack(), 1200);
      return;
    }

    if (orderId && Number(cached.id) !== orderId) {
      wx.showToast({ title: '认养信息已失效', icon: 'none' });
      setTimeout(() => wx.navigateBack(), 1200);
      return;
    }

    this.setData({
      order: normalizeOrder(cached),
      orderId: orderId || cached.id
    });
  },

  openTrace(e) {
    const sheepId = e.currentTarget.dataset.sheepId || this.data.order.primarySheepId;
    if (!sheepId) {
      wx.showToast({ title: '缺少羊只信息', icon: 'none' });
      return;
    }
    wx.navigateTo({
      url: `/packageSearch/trace/detail?sheep_id=${sheepId}`
    });
  }
});
