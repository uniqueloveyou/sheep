// pages/login/index.js
const API = require('../../utils/api.js');

Page({
  data: {
    loading: false,
  },

  onLoad() {
    // 已登录则直接跳首页
    var token = wx.getStorageSync('token');
    if (token) {
      var AUTH = require('../../utils/auth');
      AUTH.checkHasLogined().then(function (isLogined) {
        if (isLogined) {
          wx.switchTab({ url: '/pages/index/index' });
        } else {
          wx.removeStorageSync('token');
          wx.removeStorageSync('uid');
        }
      });
    }
  },

  // 核心：处理手机号授权回调
  onGetPhoneNumber(e) {
    const that = this;

    // 用户拒绝
    if (e.detail.errMsg === 'getPhoneNumber:fail user deny') {
      wx.showToast({ title: '需要授权才能登录', icon: 'none' });
      return;
    }

    // 无权限（个人号/未认证），降级为 OpenID 登录
    if (e.detail.errMsg && e.detail.errMsg.includes('no permission')) {
      console.warn('无手机号权限，使用 OpenID 备用登录');
      this.loginWithWeChatCode();
      return;
    }

    // 成功获取 phoneCode
    if (e.detail.code) {
      this.setData({ loading: true });
      wx.login({
        success: (loginRes) => {
          if (loginRes.code) {
            API.loginWithPhone({
              code: loginRes.code,
              phoneCode: e.detail.code
            }).then(res => {
              that.handleLoginSuccess(res);
            }).catch(err => {
              that.handleLoginFail(err);
            });
          }
        },
        fail: () => {
          that.setData({ loading: false });
        }
      });
    } else {
      // 未知错误，尝试备用
      wx.showModal({
        title: '提示',
        content: '获取手机号失败，是否尝试直接登录？',
        success: (res) => {
          if (res.confirm) that.loginWithWeChatCode();
        }
      });
    }
  },

  // 备用：仅 OpenID 登录
  loginWithWeChatCode() {
    const that = this;
    this.setData({ loading: true });
    wx.login({
      success: (loginRes) => {
        if (loginRes.code) {
          API.login(loginRes.code).then(res => {
            that.handleLoginSuccess(res);
          }).catch(err => {
            that.handleLoginFail(err);
          });
        }
      },
      fail: () => {
        that.setData({ loading: false });
      }
    });
  },

  // 登录成功
  handleLoginSuccess(res) {
    this.setData({ loading: false });
    if (res.code === 0) {
      var userInfo = res.data.userInfo || {};
      wx.setStorageSync('token', res.data.token);
      wx.setStorageSync('uid', userInfo.id || '');
      wx.setStorageSync('userInfo', userInfo);
      wx.showToast({ title: '登录成功' });
      setTimeout(() => {
        wx.switchTab({ url: '/pages/index/index' });
      }, 1000);
    } else {
      wx.showModal({
        title: '登录失败',
        content: res.msg || '未知错误',
        showCancel: false
      });
    }
  },

  // 登录失败
  handleLoginFail(err) {
    this.setData({ loading: false });
    const msg = err.statusCode === 404 ? '接口地址错误 (404)' : '连接服务器失败';
    wx.showToast({ title: msg, icon: 'none' });
  },

  // 暂不登录
  handleCancel() {
    wx.switchTab({ url: '/pages/index/index' });
  }
});