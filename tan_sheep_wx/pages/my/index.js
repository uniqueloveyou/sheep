// pages/my/index.js
const AUTH = require('../../utils/auth');

Page({
  data: {
    userinfo: {},  // 用户基本信息
    apiUserInfoMap: null, // 存储用户详情
    balance: 90,  // 初始余额
    freeze: 0,      // 初始冻结金额
    score: 0,       // 初始积分
    growth: 0,      // 初始关注农户
    isMock: false,  // 是否开启模拟充值
    tabs: ['资金明细', '提现记录', '押金记录'],  // 标签页
    active: 0,  // 当前激活的标签索引
    cashlogs: [], // 资金明细日志
    withDrawlogs: [], // 提现记录日志
    depositlogs: [], // 押金记录日志
    // 我的服务菜单
    serviceMenus: [
      {
        text: '个人资料',
        url: './info-menu/info-menu',
        icon: '/pages/my/images/user1.png',
        badge: ''
      },
      {
        text: '查看领养',
        url: './adopt/adopt',
        icon: '/pages/my/images/lingyang.png',
        badge: ''
      },
      {
        text: '优惠券',
        url: './youhui/youhui',
        icon: '/pages/my/images/youhui.png',
        badge: ''
      }
    ],
    // 其他功能菜单
    otherMenus: [
      {
        text: '设置',
        url: './setting',
        icon: 'setting-o',
        color: '#666',
        badge: ''
      },
      {
        text: '意见反馈',
        url: './feedback',
        icon: 'chat-o',
        color: '#666',
        badge: ''
      },
      {
        text: '关于我们',
        url: '',
        icon: 'info-o',
        color: '#666',
        badge: ''
      }
    ],
    withdrawal: '1', // 是否允许提现，'1'表示允许
    nickShow: false, // 是否显示编辑昵称弹窗
    newNick: '', // 新的昵称
  },

  onLoad() {
    // 从本地存储读取数据
    var balance = wx.getStorageSync('balance') || 90;
    var freeze = wx.getStorageSync('freeze') || 0;
    var score = wx.getStorageSync('score') || 0;
    var growth = wx.getStorageSync('growth') || 0;
    var cashlogs = wx.getStorageSync('cashlogs') || [];
    var withDrawlogs = wx.getStorageSync('withDrawlogs') || [];
    var depositlogs = wx.getStorageSync('depositlogs') || [];
    var apiUserInfoMap = wx.getStorageSync('apiUserInfoMap') || null;

    this.setData({
      balance: balance,
      freeze: freeze,
      score: score,
      growth: growth,
      cashlogs: cashlogs,
      withDrawlogs: withDrawlogs,
      depositlogs: depositlogs,
      apiUserInfoMap: apiUserInfoMap
    });

    // 检查用户是否已经登录
    AUTH.checkHasLogined().then(isLogined => {
      if (isLogined) {
        this.getUserApiInfo();
      } else {
        getApp().loginOK = () => {
          this.getUserApiInfo();
        }
      }
    });
  },

  onShow() {
    // 每次显示页面时刷新数据
    var balance = wx.getStorageSync('balance') || 90;
    var freeze = wx.getStorageSync('freeze') || 0;
    var score = wx.getStorageSync('score') || 0;
    var growth = wx.getStorageSync('growth') || 0;
    var apiUserInfoMap = wx.getStorageSync('apiUserInfoMap') || null;

    this.setData({
      balance: balance,
      freeze: freeze,
      score: score,
      growth: growth,
      apiUserInfoMap: apiUserInfoMap
    });
  },

  // 获取用户的详细信息（模拟）
  getUserApiInfo() {
    // 模拟用户信息
    var mockUserInfo = {
      base: {
        id: '123456', // 模拟用户ID
        nick: '用户昵称',
        avatarUrl: '', // 默认头像或用户选择的头像
      }
    };

    // 将模拟用户信息保存到本地存储
    wx.setStorageSync('apiUserInfoMap', mockUserInfo);

    this.setData({
      apiUserInfoMap: mockUserInfo,
      userinfo: mockUserInfo.base,
      nick: mockUserInfo.base.nick
    });
  },

  // 处理菜单项点击
  handleItemTap(e) {
    var url = e.currentTarget.dataset.url;
    if (url && url !== '') {
      wx.navigateTo({
        url: url
      });
    } else {
      // 处理特殊功能
      var text = e.currentTarget.dataset.text || '';
      if (text === '关于我们') {
        wx.showModal({
          title: '关于我们',
          content: '滩羊智品小程序\n版本：1.0.0\n\n致力于提供优质的滩羊产品和服务',
          showCancel: false,
          confirmText: '知道了'
        });
      }
    }
  },

  // 导航到登录页面
  toLogin() {
    wx.navigateTo({
      url: '/pages/login/index'
    });
  },

  // 选择头像
  onChooseAvatar(e) {
    // 使用普通方式获取 avatarUrl，避免对象解构
    var avatarUrl = e.detail.avatarUrl;
    // 手动复制对象属性，避免使用扩展运算符
    var apiUserInfoMap = this.data.apiUserInfoMap || {};
    var updatedApiUserInfoMap = {};
    
    // 复制外层属性
    for (var key in apiUserInfoMap) {
      if (apiUserInfoMap.hasOwnProperty(key)) {
        updatedApiUserInfoMap[key] = apiUserInfoMap[key];
      }
    }
    
    // 复制 base 对象
    var baseObj = apiUserInfoMap.base || {};
    updatedApiUserInfoMap.base = {};
    for (var key2 in baseObj) {
      if (baseObj.hasOwnProperty(key2)) {
        updatedApiUserInfoMap.base[key2] = baseObj[key2];
      }
    }
    // 更新 avatarUrl
    updatedApiUserInfoMap.base.avatarUrl = avatarUrl;
    this.setData({
      apiUserInfoMap: updatedApiUserInfoMap
    });
    wx.setStorageSync('apiUserInfoMap', updatedApiUserInfoMap);
    wx.showToast({
      title: '头像已更新',
      icon: 'success'
    });
  },

  // 复制用户ID
  copyUid() {
    wx.setClipboardData({
      data: this.data.apiUserInfoMap.base.id + '',
      success: () => {
        wx.showToast({
          title: '用户ID已复制',
          icon: 'success'
        });
      }
    });
  },

  // 编辑昵称
  editNick() {
    this.setData({
      nickShow: true,
      newNick: this.data.apiUserInfoMap.base.nick || ''
    });
  },

  // 监听昵称输入
  onNickInput(e) {
    this.setData({
      newNick: e.detail.value
    });
  },

  // 保存昵称
  saveNick() {
    var newNick = this.data.newNick.trim();
    if (!newNick) {
      wx.showToast({
        title: '昵称不能为空',
        icon: 'none'
      });
      return;
    }

    // 手动复制对象属性，避免使用扩展运算符
    var apiUserInfoMap = this.data.apiUserInfoMap || {};
    var updatedApiUserInfoMap = {};
    
    // 复制外层属性
    for (var key in apiUserInfoMap) {
      if (apiUserInfoMap.hasOwnProperty(key)) {
        updatedApiUserInfoMap[key] = apiUserInfoMap[key];
      }
    }
    
    // 复制 base 对象
    var baseObj = apiUserInfoMap.base || {};
    updatedApiUserInfoMap.base = {};
    for (var key2 in baseObj) {
      if (baseObj.hasOwnProperty(key2)) {
        updatedApiUserInfoMap.base[key2] = baseObj[key2];
      }
    }
    // 更新 nick
    updatedApiUserInfoMap.base.nick = newNick;

    this.setData({
      apiUserInfoMap: updatedApiUserInfoMap,
      userinfo: updatedApiUserInfoMap.base,
      nickShow: false,
      newNick: ''
    });
    wx.setStorageSync('apiUserInfoMap', updatedApiUserInfoMap);
    wx.showToast({
      title: '昵称已更新',
      icon: 'success'
    });
  },

  // 取消编辑昵称
  cancelEditNick() {
    this.setData({
      nickShow: false,
      newNick: ''
    });
  },

  // 跳转到用户二维码页面
  goUserCode() {
    wx.navigateTo({
      url: '/pages/my/user-code',
    });
  },

  // 跳转到资产页面
  goAsset() {
    wx.navigateTo({
      url: "/pages/asset/index"
    });
  },

  // 跳转到积分页面
  goScore() {
    wx.navigateTo({
      url: "/pages/score/index"
    });
  },

  // 跳转到关注农户页面
  gogrowth() {
    wx.navigateTo({
      url: '/pages/score/growth',
    });
  },

  // 跳转到登录页面
  login() {
    wx.navigateTo({
      url: '/pages/login/index',
    });
  }
});
