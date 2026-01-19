Page({
    data: {
      sheepDetail: {
        id: 1,
        title: '优质羊肉',
        price: 430.00
      },
      userInfo: {
        id: 1,
        name: '张三',
        phone: '13800000000',
        address: '',  // 默认没有地址
        virtualCurrency: 1000.00  // 用户的虚拟币余额
      },
      totalPrice: 430.00,  // 商品价格
      useVirtualCurrency: false,  // 是否使用虚拟币支付
    },
  
    onLoad() {
      // 获取用户的地址信息和虚拟币余额，假设从缓存中获取
      const savedAddress = wx.getStorageSync('userAddress');
      const userInfo = wx.getStorageSync('userInfo') || {
        id: 1,
        name: '张三',
        phone: '13800000000',
        address: '',
        virtualCurrency: 1000.00  // 示例余额
      };
      if (savedAddress) {
        userInfo.address = savedAddress;
      }
      this.setData({
        userInfo,
      });
    },
  
    selectAddress() {
      wx.navigateTo({
        url: '/pages/address/address'  
      });
    },
  
    onVirtualCurrencyToggle(e) {
      const selected = e.detail.value.length > 0;  // 如果有选中，`e.detail.value` 不为空
      this.setData({
        useVirtualCurrency: selected
      });
    },
  
    // 确认订单并支付
    confirmOrder() {
      const { userInfo, useVirtualCurrency, totalPrice } = this.data;
  
      if (!userInfo.address) {
        wx.showToast({
          title: '请先选择收货地址',
          icon: 'none'
        });
        return;
      }
  
      if (useVirtualCurrency) {
        if (userInfo.virtualCurrency >= totalPrice) {
          // 使用虚拟币支付
          this.processVirtualCurrencyPayment();
        } else {
          wx.showToast({
            title: `虚拟币余额不足，当前余额为 ${userInfo.virtualCurrency} 元`,
            icon: 'none'
          });
        }
      } else {
        // 使用微信支付
        this.processWeChatPayment();
      }
    },
  
    // 处理虚拟币支付
    processVirtualCurrencyPayment() {
      const { userInfo, sheepDetail, totalPrice } = this.data;
  
      // 显示加载提示
      wx.showLoading({
        title: '正在支付...',
        mask: true
      });
  
      // 调用后端接口来处理扣除虚拟币和生成订单
      wx.request({
        url: 'https://yourserver.com/api/pay-with-virtual-currency',  // 替换为你的后端接口
        method: 'POST',
        data: {
          userId: userInfo.id,
          productId: sheepDetail.id,
          amount: totalPrice
        },
        success: (res) => {
          wx.hideLoading();
          if (res.data.success) {
            // 更新用户虚拟币余额
            const updatedBalance = userInfo.virtualCurrency - totalPrice;
            this.setData({
              'userInfo.virtualCurrency': updatedBalance
            });
            wx.setStorageSync('userInfo', this.data.userInfo);
  
            wx.showToast({
              title: '支付成功',
              icon: 'success'
            });
            // 跳转到订单页面或其他页面
            wx.navigateTo({
              url: '/pages/order/order'
            });
          } else {
            wx.showToast({
              title: res.data.message || '支付失败',
              icon: 'none'
            });
          }
        },
        fail: () => {
          wx.hideLoading();
          wx.showToast({
            title: '网络错误，请稍后再试',
            icon: 'none'
          });
        }
      });
    },
  
    // 处理微信支付
    processWeChatPayment() {
      // 显示加载提示
      wx.showLoading({
        title: '正在支付...',
        mask: true
      });
  
      // 模拟获取支付参数
      const paymentData = {
        timeStamp: '1680000000',  // 支付时间戳
        nonceStr: 'randomString',  // 随机字符串
        package: 'prepay_id=xxx',  // 预支付订单id
        signType: 'MD5',  // 签名类型
        paySign: 'signature'  // 签名
      };
  
      // 调用支付接口
      wx.requestPayment({
        ...paymentData,
        success: (res) => {
          wx.hideLoading();
          wx.showToast({
            title: '支付成功',
            icon: 'success'
          });
          // 跳转到订单页面或其他页面
          wx.navigateTo({
            url: '/pages/order/order'
          });
        },
        fail: (res) => {
          wx.hideLoading();
          wx.showToast({
            title: '支付失败',
            icon: 'none'
          });
        }
      });
    }
  });
  