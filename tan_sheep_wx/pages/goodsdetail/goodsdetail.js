const API = require('../../utils/api.js');

Page({
    data: {
        imageList: [
            { src: '/images/icons/function/f1.png' }
        ],
        sheepDetail: {},
        isInCart: false,
        isBuyNowModalVisible: false
    },

    onLoad: function (options) {
        if (options.id) {
            var sheepId = options.id;
            this.setData({ sheepId: sheepId });
            this.loadData(sheepId);
        } else {
            wx.showToast({
                title: '无效的羊只ID',
                icon: 'error'
            });
        }
    },

    loadData: function (sheepId) {
        this.getSheepDetail(sheepId);
    },

    getSheepDetail: function (sheepId) {
        var that = this;

        API.request(`/api/sheep/${sheepId}`, 'GET')
            .then((res) => {
                var sheepDetail = res || {};
                var rawDailyCareFee = parseFloat(sheepDetail.daily_care_fee);
                sheepDetail.dailyCareFeeText = isNaN(rawDailyCareFee) ? '10.00' : rawDailyCareFee.toFixed(2);
                that.setData({
                    sheepDetail: sheepDetail
                });
            })
            .catch((error) => {
                console.error('[获取羊只详情] 请求失败:', error);
                wx.showToast({
                    title: '羊信息获取失败',
                    icon: 'none',
                    duration: 2000
                });
            });
    },

    openBuyNowModal: function () {
        this.setData({
            isBuyNowModalVisible: true
        });
    },

    closeBuyNowModal: function () {
        this.setData({
            isBuyNowModalVisible: false
        });
    },

    confirmBuyNow: function () {
        var sheepDetail = this.data.sheepDetail;
        wx.navigateTo({
            url: '/packageOrder/cart/checkout?sheepId=' + sheepDetail.id
        });
        this.closeBuyNowModal();
    },

    addToCart: function () {
        var that = this;
        var sheepDetail = this.data.sheepDetail;

        API.request('/api/cart', 'POST', {
            sheep_id: sheepDetail.id,
            price: sheepDetail.price
        }, function(res) {
            that.setData({ isInCart: true });
            wx.showToast({
                title: '已加入购物车',
                icon: 'success',
                duration: 2000
            });
        }, function(err) {
            wx.showToast({
                title: '加入购物车失败',
                icon: 'none',
                duration: 2000
            });
        });
    }
});
