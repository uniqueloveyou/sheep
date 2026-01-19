// pages/login/index.js
const API = require('../../utils/api.js');

Page({
  data: {
    loading: false,
    isRegister: false,  // 是否为注册模式
    username: '',
    password: '',
    confirmPassword: '',  // 确认密码
    mobile: '',  // 手机号（可选）
    nickname: ''  // 昵称（可选）
  },

  onLoad() {
    // 暂时不需要强制登录，如果已登录则自动跳转
    var token = wx.getStorageSync('token');
    if (token) {
      // 验证 token 是否有效
      var AUTH = require('../../utils/auth');
      var that = this;
      AUTH.checkHasLogined().then(function(isLogined) {
        if (isLogined) {
          // token 有效，跳转到首页
          setTimeout(function() {
            wx.switchTab({ url: '/pages/index/index' });
          }, 500);
        } else {
          // token 无效，清除并停留在登录页
          wx.removeStorageSync('token');
          wx.removeStorageSync('uid');
        }
      });
    }
    // 如果没有 token，停留在登录页（用户可以继续使用其他功能）
  },

  // --- 核心：处理手机号获取 ---
  onGetPhoneNumber(e) {
    const that = this;
    console.log('手机号回调:', e);

    // 情况 A: 用户拒绝
    if (e.detail.errMsg === "getPhoneNumber:fail user deny") {
      wx.showToast({ title: '需要授权才能登录', icon: 'none' });
      return;
    }

    // 情况 B: 权限不足 (如个人号或未认证)，降级为普通微信登录
    if (e.detail.errMsg && e.detail.errMsg.includes('no permission')) {
      console.warn('无手机号权限，尝试备用登录方案');
      this.loginWithWeChatCode();
      return;
    }

    // 情况 C: 成功获取手机号 code
    if (e.detail.code) {
      this.setData({ loading: true });
      const phoneCode = e.detail.code; // 手机号解密用

      // 同时获取登录 code (用于换 openid)
      wx.login({
        success: (loginRes) => {
          if (loginRes.code) {
            // 调用后端接口
            API.loginWithPhone({
              code: loginRes.code,     // 换 OpenID
              phoneCode: phoneCode     // 换手机号
            }).then(res => {
              that.handleLoginSuccess(res);
            }).catch(err => {
              that.handleLoginFail(err);
            });
          }
        },
        fail: (err) => {
          that.setData({ loading: false });
          console.error('wx.login 失败:', err);
        }
      });
    } else {
      // 其他未知错误
      wx.showModal({
        title: '提示',
        content: '获取手机号失败，是否尝试直接登录？',
        success: (res) => {
          if (res.confirm) that.loginWithWeChatCode();
        }
      });
    }
  },

  // --- 备用方案：仅使用 OpenID 登录 ---
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
      fail: (err) => {
        that.setData({ loading: false });
      }
    });
  },

  // --- 统一处理登录成功 ---
  handleLoginSuccess(res) {
    var that = this;
    this.setData({ loading: false });
    if (res.code === 0) {
      wx.setStorageSync('token', res.data.token);
      wx.setStorageSync('uid', res.data.uid);
      
      // 保存用户信息（兼容不同接口返回格式）
      var userInfo = res.data.userInfo || {
        id: res.data.uid,
        username: res.data.username || '',
        nickname: res.data.nickname || '',
        mobile: res.data.mobile || ''
      };
      wx.setStorageSync('userInfo', userInfo);
      
      wx.showToast({ title: '登录成功' });
      setTimeout(function() {
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

  // --- 统一处理登录失败 ---
  handleLoginFail(err) {
    this.setData({ loading: false });
    console.error('登录请求出错:', err);
    
    let errorMsg = '连接服务器失败';
    // 如果是 404，说明后端路由没配置对
    if (err.statusCode === 404) {
      errorMsg = '接口地址错误 (404)';
    }

    wx.showToast({ title: errorMsg, icon: 'none' });
  },

  // --- 暂不登录 ---
  handleCancel() {
    wx.switchTab({ url: '/pages/index/index' });
  },

  // --- 用户名输入 ---
  onUsernameInput(e) {
    this.setData({
      username: e.detail.value
    });
  },

  // --- 密码输入 ---
  onPasswordInput(e) {
    this.setData({
      password: e.detail.value
    });
  },

  // --- 切换登录/注册模式 ---
  toggleMode() {
    this.setData({
      isRegister: !this.data.isRegister,
      username: '',
      password: '',
      confirmPassword: '',
      mobile: '',
      nickname: ''
    });
  },

  // --- 确认密码输入 ---
  onConfirmPasswordInput(e) {
    this.setData({
      confirmPassword: e.detail.value
    });
  },

  // --- 手机号输入 ---
  onMobileInput(e) {
    this.setData({
      mobile: e.detail.value
    });
  },

  // --- 昵称输入 ---
  onNicknameInput(e) {
    this.setData({
      nickname: e.detail.value
    });
  },

  // --- 用户注册 ---
  onRegister() {
    var that = this;
    var username = this.data.username.trim();
    var password = this.data.password.trim();
    var confirmPassword = this.data.confirmPassword.trim();
    var mobile = this.data.mobile.trim();
    var nickname = this.data.nickname.trim();

    // 验证输入
    if (!username) {
      wx.showToast({
        title: '请输入用户名',
        icon: 'none'
      });
      return;
    }

    if (username.length < 3 || username.length > 50) {
      wx.showToast({
        title: '用户名长度为3-50个字符',
        icon: 'none'
      });
      return;
    }

    if (!password) {
      wx.showToast({
        title: '请输入密码',
        icon: 'none'
      });
      return;
    }

    if (password.length < 6) {
      wx.showToast({
        title: '密码长度至少6个字符',
        icon: 'none'
      });
      return;
    }

    if (password !== confirmPassword) {
      wx.showToast({
        title: '两次密码输入不一致',
        icon: 'none'
      });
      return;
    }

    // 设置加载状态
    this.setData({ loading: true });

    // 调用后端接口
    API.register(username, password, mobile || null, nickname || null)
      .then(function(res) {
        that.handleRegisterSuccess(res);
      })
      .catch(function(err) {
        that.handleRegisterFail(err);
      });
  },

  // --- 处理注册成功 ---
  handleRegisterSuccess(res) {
    var that = this;
    this.setData({ loading: false });
    if (res.code === 0) {
      wx.setStorageSync('token', res.data.token);
      wx.setStorageSync('uid', res.data.uid);
      
      // 保存用户信息
      var userInfo = res.data.userInfo || {
        id: res.data.uid,
        username: res.data.username || '',
        nickname: res.data.nickname || '',
        mobile: res.data.mobile || ''
      };
      wx.setStorageSync('userInfo', userInfo);
      
      wx.showToast({ title: '注册成功' });
      setTimeout(function() {
        wx.switchTab({ url: '/pages/index/index' });
      }, 1000);
    } else {
      wx.showModal({
        title: '注册失败',
        content: res.msg || '未知错误',
        showCancel: false
      });
    }
  },

  // --- 处理注册失败 ---
  handleRegisterFail(err) {
    this.setData({ loading: false });
    console.error('注册请求出错:', err);
    
    var errorMsg = '连接服务器失败';
    if (err.statusCode === 404) {
      errorMsg = '接口地址错误 (404)';
    } else if (err.statusCode === 409) {
      errorMsg = err.response && err.response.msg ? err.response.msg : '用户名或手机号已被注册';
    } else if (err.response && err.response.msg) {
      errorMsg = err.response.msg;
    }

    wx.showToast({ title: errorMsg, icon: 'none', duration: 2000 });
  },

  // --- 用户名密码登录 ---
  onPasswordLogin() {
    var that = this;
    var username = this.data.username.trim();
    var password = this.data.password.trim();

    // 验证输入
    if (!username) {
      wx.showToast({
        title: '请输入用户名或手机号',
        icon: 'none'
      });
      return;
    }

    if (!password) {
      wx.showToast({
        title: '请输入密码',
        icon: 'none'
      });
      return;
    }

    // 设置加载状态
    this.setData({ loading: true });

    // 调用后端接口
    API.loginWithPassword(username, password).then(function(res) {
      that.handleLoginSuccess(res);
    }).catch(function(err) {
      that.handleLoginFail(err);
    });
  }
});