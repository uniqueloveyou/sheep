const WXAPI = require('apifm-wxapi'); // 引入接口
const app = getApp(); // 获取应用实例

Page({
  data: {
    amount: '', // 充值金额
    balance: 0.00, // 当前余额
    isMock: true, // 是否开启模拟充值
  },

  onLoad: function () {
    // 页面加载时，从本地存储获取余额
    const balance = wx.getStorageSync('balance') || 0.00;
    this.setData({ balance });
  },
  bindSave: function (e) {
    const that = this;
    const amount = e.detail.value.amount; // 获取用户输入的充值金额
  
    // 判断充值金额是否合法
    if (amount === "" || amount * 1 <= 0) {
      wx.showModal({
        title: '错误',
        content: '请输入有效的充值金额',
        showCancel: false
      });
      return;
    }
  
    // 检查是否开启模拟充值模式
    if (this.data.isMock) {
      // 模拟充值：直接增加余额
      const newBalance = parseFloat(this.data.balance) + parseFloat(amount);
      this.setData({
        balance: newBalance.toFixed(2) // 保留两位小数
      });
      wx.showModal({
        title: '成功',
        content: '充值成功',
        showCancel: false
      });
      // 更新本地存储的余额
      wx.setStorageSync('balance', newBalance.toFixed(2));
      return; // 结束函数执行
    }
  
    // 如果不开启模拟充值，调用后台接口更新余额
    WXAPI.payDeposit({
      token: wx.getStorageSync('token'),
      amount: amount
    }).then(res => {
      if (res.code != 0) {
        wx.showModal({
          title: '错误',
          content: res.msg,
          showCancel: false
        });
        return;
      }
  
      // 后台支付成功后，更新余额
      const newBalance = parseFloat(this.data.balance) + parseFloat(amount);
      this.setData({
        balance: newBalance.toFixed(2)
      });
      wx.showModal({
        title: '成功',
        content: '充值成功',
        showCancel: false
      });
      wx.setStorageSync('balance', newBalance.toFixed(2)); // 更新本地存储
    }).catch(err => {
      wx.showModal({
        title: '请求失败',
        content: '充值失败，请稍后再试',
        showCancel: false
      });
    });
  },

  // 提供一个方法来切换模拟充值的状态
  toggleMock: function () {
    this.setData({ isMock: !this.data.isMock });
  }
});
