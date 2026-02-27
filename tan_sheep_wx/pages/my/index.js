// pages/my/index.js
const AUTH = require('../../utils/auth');
const API = require('../../utils/api.js');

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
        url: '/pages/my/info',
        icon: '/pages/my/images/user1.png',
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
        text: '申请养殖户',
        url: '',
        icon: 'friends-o',
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

    applyBreederShow: false, // 申请养殖户弹窗
    applyMobile: '', // 申请手机号
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

    this.setData({
      balance: balance,
      freeze: freeze,
      score: score,
      growth: growth,
    });

    // 每次显示都刷新用户信息（解决登录后切回仍显示未登录的问题）
    var token = wx.getStorageSync('token');
    if (token) {
      this.getUserApiInfo();
    } else {
      this.setData({ apiUserInfoMap: null });
    }

    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      const tabBar = this.getTabBar();
      tabBar.initTabBar();
      const index = tabBar.data.list.findIndex(item => item.pagePath === "/pages/my/index");
      if (index > -1) {
        tabBar.setData({ selected: index });
      }
    }
  },

  // 获取用户的详细信息
  async getUserApiInfo() {
    var token = wx.getStorageSync('token');
    if (token) {
      try {
        const res = await API.getUserInfo(token);
        if (res.code === 0) {
          const info = res.data;
          // 同时缓存到本地，保持同步
          wx.setStorageSync('userInfo', info);

          var userInfoMap = {
            base: {
              id: info.id || '',
              nick: info.nickname || info.username || '未设置昵称',
              avatarUrl: info.avatar_url || '',
              mobile: info.mobile || '',
              username: info.username || '',
              role: info.role || 0,
              is_verified: info.is_verified || false
            }
          };

          wx.setStorageSync('apiUserInfoMap', userInfoMap);

          // 真实获取余额和累计消费
          var realBalance = info.balance !== undefined ? parseFloat(info.balance).toFixed(2) : '0.00';
          var realConsumed = info.total_consumed !== undefined ? parseFloat(info.total_consumed).toFixed(2) : '0.00';

          wx.setStorageSync('balance', realBalance);
          wx.setStorageSync('freeze', realConsumed);

          this.setData({
            apiUserInfoMap: userInfoMap,
            userinfo: userInfoMap.base,
            nick: userInfoMap.base.nick,
            balance: realBalance,
            freeze: realConsumed
          });
        }
      } catch (e) {
        console.error('获取用户信息失败', e);
      }
    }
  },

  // 申请养殖户 手机号输入变更
  onApplyMobileInput(e) {
    this.setData({ applyMobile: e.detail.value });
  },

  // 取消申请养殖户
  cancelApplyBreeder() {
    this.setData({ applyBreederShow: false });
  },

  // 提交申请养殖户
  async submitApplyBreeder() {
    const mobile = this.data.applyMobile;
    if (!mobile || mobile.length !== 11) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' });
      return;
    }

    const token = wx.getStorageSync('token');
    wx.showLoading({ title: '提交中' });
    try {
      const res = await API.applyBreeder(token, mobile);
      wx.hideLoading();
      if (res.code === 0) {
        wx.showToast({ title: '申请已提交', icon: 'success' });
        this.setData({ applyBreederShow: false });
        // 刷新状态
        this.getUserApiInfo();
      } else {
        wx.showToast({ title: res.msg || '提交失败', icon: 'none' });
      }
    } catch (e) {
      wx.hideLoading();
      wx.showToast({ title: '网络错误', icon: 'none' });
    }
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
      if (text === '申请养殖户') {
        const info = this.data.apiUserInfoMap ? this.data.apiUserInfoMap.base : {};
        if (info.role === 1 || info.role === 2) {
          if (info.role === 1 && !info.is_verified) {
            wx.showToast({ title: '申请正在审核中', icon: 'none' });
          } else if (info.role === 1 && info.is_verified) {
            wx.showToast({ title: '您已是养殖户', icon: 'none' });
          } else {
            wx.showToast({ title: '您是管理员', icon: 'none' });
          }
        } else {
          // 普通用户且未申请，弹窗输入手机号
          this.setData({
            applyBreederShow: true,
            applyMobile: info.mobile || ''
          });
        }
      } else if (text === '关于我们') {
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

  // 选择头像并直传 R2
  async onChooseAvatar(e) {
    var avatarUrl = e.detail.avatarUrl;
    var token = wx.getStorageSync('token');
    if (!token) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '正在上传' });

    try {
      // 1. 获取预签名 URL
      var extMatch = avatarUrl.match(/\.([^.]+)$/);
      var ext = extMatch ? '.' + extMatch[1].toLowerCase() : '.jpg';
      var contentType = ext === '.png' ? 'image/png' : 'image/jpeg';

      const signRes = await API.getAvatarUploadUrl(token, ext, contentType);
      if (signRes.code !== 0) {
        throw new Error(signRes.msg || '获取上传链接失败');
      }

      const { upload_url, object_key } = signRes.data;

      // 2. 读取文件为 ArrayBuffer
      const fs = wx.getFileSystemManager();
      const fileData = await new Promise((resolve, reject) => {
        fs.readFile({
          filePath: avatarUrl,
          success: (res) => resolve(res.data),
          fail: (err) => reject(new Error('读取文件失败'))
        });
      });

      // 3. PUT 请求直传到 R2
      await new Promise((resolve, reject) => {
        wx.request({
          url: upload_url,
          method: 'PUT',
          data: fileData,
          header: {
            'Content-Type': contentType
          },
          success: (res) => {
            if (res.statusCode === 200) resolve();
            else reject(new Error('直传 R2 失败, HTTP状态码: ' + res.statusCode));
          },
          fail: (err) => reject(new Error('直传请求失败'))
        });
      });

      // 4. 确认上传并更新个人资料
      const confirmRes = await API.confirmAvatarUpload(token, object_key);
      if (confirmRes.code !== 0) {
        throw new Error(confirmRes.msg || '确认上传失败');
      }

      // 5. 更新本地缓存和页面显示
      var updatedUser = confirmRes.data;
      var apiUserInfoMap = this.data.apiUserInfoMap || {};

      // 手动复制对象属性，避免浅拷贝问题
      var updatedApiUserInfoMap = {};
      for (var key in apiUserInfoMap) {
        if (apiUserInfoMap.hasOwnProperty(key)) {
          updatedApiUserInfoMap[key] = apiUserInfoMap[key];
        }
      }
      var baseObj = apiUserInfoMap.base || {};
      updatedApiUserInfoMap.base = {};
      for (var key2 in baseObj) {
        if (baseObj.hasOwnProperty(key2)) {
          updatedApiUserInfoMap.base[key2] = baseObj[key2];
        }
      }

      // 设置新的头像
      updatedApiUserInfoMap.base.avatarUrl = updatedUser.avatar_url;

      this.setData({
        apiUserInfoMap: updatedApiUserInfoMap
      });
      wx.setStorageSync('apiUserInfoMap', updatedApiUserInfoMap);

      // 同时更新 userInfo storage
      var storedInfo = wx.getStorageSync('userInfo') || {};
      storedInfo.avatar_url = updatedUser.avatar_url;
      wx.setStorageSync('userInfo', storedInfo);

      wx.hideLoading();
      wx.showToast({ title: '头像已更新', icon: 'success' });

    } catch (error) {
      wx.hideLoading();
      wx.showToast({ title: error.message || '上传失败', icon: 'none' });
      console.error('头像上传错误:', error);
    }
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

  // 微信直接获取昵称回调（失焦时触发）
  onNickBlur(e) {
    if (e.detail.value) {
      this.setData({
        newNick: e.detail.value
      });
    }
  },

  // 保存昵称
  async saveNick() {
    var newNick = this.data.newNick.trim();
    if (!newNick) {
      wx.showToast({
        title: '昵称不能为空',
        icon: 'none'
      });
      return;
    }

    var token = wx.getStorageSync('token');
    if (!token) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      return;
    }

    wx.showLoading({ title: '保存中' });

    try {
      // 1. 调用后端更新资料接口
      const res = await API.updateUserInfo(token, newNick);
      if (res.code !== 0) {
        throw new Error(res.msg || '更新昵称失败');
      }

      // 2. 更新本地缓存
      var updatedUser = res.data;
      var apiUserInfoMap = this.data.apiUserInfoMap || {};

      var updatedApiUserInfoMap = {};
      for (var key in apiUserInfoMap) {
        if (apiUserInfoMap.hasOwnProperty(key)) {
          updatedApiUserInfoMap[key] = apiUserInfoMap[key];
        }
      }
      var baseObj = apiUserInfoMap.base || {};
      updatedApiUserInfoMap.base = {};
      for (var key2 in baseObj) {
        if (baseObj.hasOwnProperty(key2)) {
          updatedApiUserInfoMap.base[key2] = baseObj[key2];
        }
      }

      updatedApiUserInfoMap.base.nick = updatedUser.nickname;

      this.setData({
        apiUserInfoMap: updatedApiUserInfoMap,
        userinfo: updatedApiUserInfoMap.base,
        nickShow: false,
        newNick: ''
      });

      wx.setStorageSync('apiUserInfoMap', updatedApiUserInfoMap);

      var storedInfo = wx.getStorageSync('userInfo') || {};
      storedInfo.nickname = updatedUser.nickname;
      wx.setStorageSync('userInfo', storedInfo);

      wx.hideLoading();
      wx.showToast({ title: '昵称已更新', icon: 'success' });

    } catch (error) {
      wx.hideLoading();
      wx.showToast({ title: error.message || '保存失败', icon: 'none' });
    }
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
  },

  // 退出登录
  onLogout() {
    wx.showModal({
      title: '提示',
      content: '确定退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          // 清除所有登录相关缓存
          wx.removeStorageSync('token');
          wx.removeStorageSync('uid');
          wx.removeStorageSync('userInfo');
          wx.removeStorageSync('apiUserInfoMap');

          // 刷新页面为未登录状态
          this.setData({
            apiUserInfoMap: null,
            userinfo: {},
          });

          wx.showToast({ title: '已退出登录', icon: 'success' });
        }
      }
    });
  }
});
