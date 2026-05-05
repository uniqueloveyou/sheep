// pages/search/index.js
const API = require('../../utils/api.js');

Page({
  data: {
    searchKeyword: '', // 搜索关键词
    isFocus: false, // 是否聚焦搜索框
    hasSearched: false, // 是否已搜索
    historyList: [], // 历史搜索记录
    resultList: [], // 搜索结果列表
    showFilterPopup: false, // 是否显示筛选弹窗
    // 筛选选项
    genderOptions: [
      { label: '全部', value: '' },
      { label: '雄性', value: '雄性' },
      { label: '雌性', value: '雌性' }
    ],
    priceRanges: [
      { label: '全部', value: '' },
      { label: '0-300元', value: '0-300' },
      { label: '300-500元', value: '300-500' },
      { label: '500-800元', value: '500-800' },
      { label: '800元以上', value: '800-' }
    ],
    selectedGender: '', // 选中的性别
    selectedPriceRange: '', // 选中的价格区间
    originalResults: [] // 原始搜索结果（用于筛选）
  },

  onLoad(options) {
    // 如果有传入关键词，直接搜索
    if (options.keyword) {
      this.setData({
        searchKeyword: options.keyword,
        isFocus: true
      });
      this.performSearch(options.keyword);
    } else {
      // 加载历史搜索记录
      this.loadHistory();
    }
  },

  onShow() {
    // 每次显示页面时，如果不是搜索状态，重新加载历史记录
    if (!this.data.hasSearched) {
      this.loadHistory();
    }
  },

  // 加载历史搜索记录
  loadHistory() {
    const history = wx.getStorageSync('searchHistory') || [];
    this.setData({
      historyList: history.slice(0, 10) // 最多显示10条
    });
  },

  // 输入框输入事件
  onInput(e) {
    const value = e.detail.value;
    this.setData({
      searchKeyword: value
    });
  },

  // 清除输入
  clearInput() {
    this.setData({
      searchKeyword: '',
      hasSearched: false,
      resultList: []
    });
  },

  // 搜索
  onSearch(e) {
    const keyword = e.detail.value || this.data.searchKeyword;
    if (!keyword.trim()) {
      wx.showToast({
        title: '请输入搜索关键词',
        icon: 'none'
      });
      return;
    }
    this.performSearch(keyword);
  },

  // 执行搜索
  performSearch(keyword) {
    if (!keyword.trim()) return;

    // 保存搜索历史
    this.saveHistory(keyword);

    // 显示加载
    wx.showLoading({
      title: '搜索中...',
      mask: true
    });

    // 调用搜索API
    API.request('/search_goods', 'GET', {
      keyword: keyword.trim()
    })
      .then((res) => {
        wx.hideLoading();
        const results = Array.isArray(res) ? res : [];
        results.forEach((item) => {
          const rawDailyCareFee = parseFloat(item && item.daily_care_fee);
          item.dailyCareFeeText = isNaN(rawDailyCareFee) ? '' : rawDailyCareFee.toFixed(2);
        });
        this.setData({
          resultList: results,
          originalResults: results,
          hasSearched: true,
          searchKeyword: keyword
        });
      })
      .catch((err) => {
        wx.hideLoading();
        console.error('搜索请求失败:', err);

        this.setData({
          resultList: [],
          originalResults: [],
          hasSearched: true,
          searchKeyword: keyword
        });
      });
  },

  // 通过历史记录搜索
  searchByHistory(e) {
    const keyword = e.currentTarget.dataset.keyword;
    this.setData({
      searchKeyword: keyword,
      isFocus: true
    });
    this.performSearch(keyword);
  },

  // 保存搜索历史
  saveHistory(keyword) {
    let history = wx.getStorageSync('searchHistory') || [];
    // 移除重复项
    history = history.filter(item => item !== keyword);
    // 添加到开头
    history.unshift(keyword);
    // 最多保存20条
    history = history.slice(0, 20);
    wx.setStorageSync('searchHistory', history);
    this.setData({
      historyList: history.slice(0, 10)
    });
  },

  // 清除历史记录
  clearHistory() {
    wx.showModal({
      title: '提示',
      content: '确定要清除所有搜索历史吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('searchHistory');
          this.setData({
            historyList: []
          });
          wx.showToast({
            title: '已清除',
            icon: 'success'
          });
        }
      }
    });
  },

  // 取消搜索
  onCancel() {
    wx.navigateBack();
  },

  /**
   * 解析扫码结果，兼容耳标号、sheep_id 和完整溯源 URL
   */
  resolveTraceTarget(scanResult) {
    const rawValue = String(scanResult || '').trim();
    if (!rawValue) {
      return null;
    }

    const normalizedValue = API.normalizeEarTag(rawValue);
    const traceUrlMatch = normalizedValue.match(/\/(?:api\/public\/)?trace\/(\d+)(?:\/)?(?:[?#].*)?$/i);
    if (traceUrlMatch) {
      return { sheepId: traceUrlMatch[1] };
    }

    const sheepIdQueryMatch = normalizedValue.match(/[?&](?:sheep_id|id)=(\d+)/i);
    if (sheepIdQueryMatch) {
      return { sheepId: sheepIdQueryMatch[1] };
    }

    if (/^\d+$/.test(normalizedValue)) {
      return { sheepId: normalizedValue };
    }

    const earTagQueryMatch = normalizedValue.match(/[?&]ear_tag=([^&#]+)/i);
    if (earTagQueryMatch) {
      const earTagFromQuery = API.normalizeEarTag(decodeURIComponent(earTagQueryMatch[1]));
      if (API.isValidEarTag(earTagFromQuery)) {
        return { earTag: earTagFromQuery };
      }
    }

    if (API.isValidEarTag(normalizedValue)) {
      return { earTag: normalizedValue };
    }

    return null;
  },

  /**
   * 扫描二维码进行溯源查询
   * 功能：调用微信原生扫码接口，支持相册选择和二维码/条形码
   * 扫码成功后跳转到溯源详情页，传递耳标编号
   */
  onScanQRCode() {
    console.log('[扫码溯源] 开始扫码');

    // 开发环境调试：提供手动输入选项
    const that = this;
    wx.showModal({
      title: '扫码溯源',
      content: '扫码或手动输入耳标编号',
      confirmText: '扫码',
      cancelText: '手动输入',
      success: (res) => {
        if (res.confirm) {
          that.realScanCode();
        } else if (res.cancel) {
          that.manualInputEarTag();
        }
      }
    });
  },

  /**
   * 手动输入耳标编号（开发调试用）
   */
  manualInputEarTag() {
    wx.showModal({
      title: '输入耳标编号',
      editable: true,
      success: (inputRes) => {
        if (inputRes.confirm && inputRes.content) {
          const earTag = API.normalizeEarTag(inputRes.content);
          if (!API.isValidEarTag(earTag)) {
            wx.showToast({
              title: '输入格式有误，请重新输入',
              icon: 'none',
              duration: 2000
            });
            return;
          }
          console.log('[扫码溯源] 手动输入耳标:', earTag);
          this.jumpToTraceDetail(earTag);
        }
      }
    });
  },

  /**
   * 真实扫码功能
   */
  realScanCode() {
    wx.scanCode({
      // 支持从相册选择二维码图片
      onlyFromCamera: false,
      // 支持二维码和条形码
      scanType: ['qrCode', 'barCode'],
      success: (res) => {
        console.log('[扫码溯源] 扫码成功', res);

        const traceTarget = this.resolveTraceTarget(res.result);
        if (!traceTarget) {
          wx.showToast({
            title: '无法识别溯源码',
            icon: 'none',
            duration: 2000
          });
          console.warn('[扫码溯源] 无法解析扫码结果:', res.result);
          return;
        }

        console.log('[扫码溯源] 解析后的目标:', traceTarget);
        this.jumpToTraceDetail(traceTarget);
      },
      fail: (err) => {
        // 用户取消扫码，不显示错误提示
        if (err.errMsg && err.errMsg.indexOf('cancel') !== -1) {
          console.log('[扫码溯源] 用户取消扫码');
          return;
        }

        console.error('[扫码溯源] 扫码失败:', err);
        wx.showToast({
          title: '扫码功能仅支持真机',
          icon: 'none',
          duration: 3000
        });
      }
    });
  },

  /**
   * 跳转到溯源详情页
   */
  jumpToTraceDetail(target) {
    const traceTarget = typeof target === 'string'
      ? { earTag: API.normalizeEarTag(target) }
      : (target || {});

    let url = '';
    if (traceTarget.sheepId) {
      url = `/packageSearch/trace/detail?sheep_id=${encodeURIComponent(traceTarget.sheepId)}`;
    } else if (traceTarget.earTag && API.isValidEarTag(traceTarget.earTag)) {
      url = `/packageSearch/trace/detail?ear_tag=${encodeURIComponent(traceTarget.earTag)}`;
    } else {
      wx.showToast({
        title: '输入格式有误，请重新输入',
        icon: 'none',
        duration: 2000
      });
      return;
    }

    wx.navigateTo({
      url,
      success: () => {
        console.log('[扫码溯源] 成功跳转到溯源详情页');
      },
      fail: (err) => {
        console.error('[扫码溯源] 跳转失败:', err);
        wx.showToast({
          title: '页面跳转失败',
          icon: 'none',
          duration: 2000
        });
      }
    });
  },
  fail: (err) => {
    // 用户取消扫码，只打印日志，不显示错误提示
    if (err.errMsg && err.errMsg.indexOf('cancel') !== -1) {
      console.log('[扫码溯源] 用户取消扫码');
      return;
    }


    // 其他错误，显示提示
    console.error('[扫码溯源] 扫码失败:', err);
    wx.showToast({
      title: '扫码失败，请重试',
      icon: 'none',
      duration: 2000
    });
  },

  // 显示筛选弹窗
  showFilter() {
    this.setData({
      showFilterPopup: true
    });
  },

  // 关闭筛选弹窗
  closeFilter() {
    this.setData({
      showFilterPopup: false
    });
  },

  // 选择性别
  selectGender(e) {
    const value = e.currentTarget.dataset.value;
    this.setData({
      selectedGender: value
    });
  },

  // 选择价格区间
  selectPriceRange(e) {
    const value = e.currentTarget.dataset.value;
    this.setData({
      selectedPriceRange: value
    });
  },

  // 重置筛选
  resetFilter() {
    this.setData({
      selectedGender: '',
      selectedPriceRange: ''
    });
    this.applyFilter();
  },

  // 应用筛选
  applyFilter() {
    // 使用 slice() 复制数组，避免使用扩展运算符
    var originalResults = this.data.originalResults || [];
    var results = originalResults.slice(0);

    // 性别筛选
    if (this.data.selectedGender) {
      results = results.filter(function (item) {
        return item.gender === this.data.selectedGender;
      }.bind(this));
    }

    // 价格区间筛选
    if (this.data.selectedPriceRange) {
      var range = this.data.selectedPriceRange;
      if (range.indexOf('-') !== -1) {
        // 使用 split 后再取数组元素，避免数组解构
        var parts = range.split('-');
        var min = parts[0];
        var max = parts[1];
        results = results.filter(function (item) {
          var price = item.price || 0;
          return price >= parseFloat(min) && (max ? price <= parseFloat(max) : true);
        });
      } else if (range.charAt(range.length - 1) === '-') {
        var min = parseFloat(range.replace('-', ''));
        results = results.filter(function (item) {
          return (item.price || 0) >= min;
        });
      }
    }

    this.setData({
      resultList: results,
      showFilterPopup: false
    });
  },

  // 跳转到详情页
  goToDetail(e) {
    const id = e.currentTarget.dataset.id;
    const type = e.currentTarget.dataset.type || 'sheep';

    let url = '';
    if (type === 'sheep') {
      // 跳转到溯源详情页，展示完整的羊只信息
      url = `/packageSearch/trace/detail?id=${id}`;
    } else if (type === 'breeder') {
      // 跳转到养殖户详情页
      url = `/pages/breeder/my1/my1?id=${id}`;
    } else {
      // 默认跳转到羊只溯源详情页
      url = `/packageSearch/trace/detail?id=${id}`;
    }

    wx.navigateTo({
      url: url
    });
  }
});


