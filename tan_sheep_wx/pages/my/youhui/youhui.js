// pages/my/youhui/youhui.js
const API = require('../../utils/api.js');
const AUTH = require('../../utils/auth.js');

Page({
    data: {
        coupons: [],  // 用户已领取的优惠券列表
        unusedCoupons: [],  // 未使用的优惠券
        usedCoupons: [],  // 已使用的优惠券
        expiredCoupons: [],  // 已过期的优惠券
        currentCoupons: [],  // 当前显示的优惠券
        loading: false,
        userInfo: null,
        activeTab: 'unused',  // unused: 未使用, used: 已使用, expired: 已过期
    },

    onLoad(options) {
        this.loadUserInfo();
    },

    onShow() {
        // 每次显示页面时刷新数据
        if (this.data.userInfo && this.data.userInfo.uid) {
            this.loadUserCoupons();
        } else {
            this.loadUserInfo();
        }
    },

    onPullDownRefresh() {
        this.loadUserCoupons().finally(() => {
            wx.stopPullDownRefresh();
        });
    },

    // 加载用户信息
    loadUserInfo() {
        const userInfo = AUTH.getUserInfo();
        if (userInfo && userInfo.uid) {
            this.setData({ userInfo });
            // 加载用户优惠券
            this.loadUserCoupons();
        } else {
            wx.showModal({
                title: '提示',
                content: '请先登录',
                success: (res) => {
                    if (res.confirm) {
                        wx.navigateTo({
                            url: '/pages/login/index'
                        });
                    } else {
                        wx.navigateBack();
                    }
                }
            });
        }
    },

    // 加载用户优惠券
    loadUserCoupons() {
        const userInfo = this.data.userInfo;
        if (!userInfo || !userInfo.uid) {
            return Promise.resolve();
        }

        this.setData({ loading: true });

        return API.request(`/api/promotions/coupons?user_id=${userInfo.uid}`, 'GET')
            .then(res => {
                console.log('用户优惠券数据:', res);
                if (res.code === 0 && res.data) {
                    // 按状态分类
                    const unused = res.data.filter(c => c.status === 'unused');
                    const used = res.data.filter(c => c.status === 'used');
                    const expired = res.data.filter(c => c.status === 'expired');

                    // 预处理优惠券数据，添加显示文本
                    const processCoupons = (list) => {
                        return list.map(coupon => {
                            return {
                                ...coupon,
                                displayText: this.getCouponDisplayText(coupon)
                            };
                        });
                    };

                    this.setData({
                        coupons: res.data,
                        unusedCoupons: processCoupons(unused),
                        usedCoupons: processCoupons(used),
                        expiredCoupons: processCoupons(expired),
                        loading: false
                    });
                    // 更新当前显示的优惠券
                    this.updateCurrentCoupons(this.data.activeTab);
                } else {
                    wx.showToast({
                        title: res.msg || '加载失败',
                        icon: 'none'
                    });
                    this.setData({ loading: false });
                }
            })
            .catch(error => {
                console.error('加载用户优惠券失败:', error);
                wx.showToast({
                    title: '加载失败: ' + (error.message || '未知错误'),
                    icon: 'none'
                });
                this.setData({ loading: false });
            });
    },

    // 切换标签
    changeTab(e) {
        const tab = e.currentTarget.dataset.tab;
        this.updateCurrentCoupons(tab);
        this.setData({
            activeTab: tab
        });
    },

    // 更新当前显示的优惠券列表
    updateCurrentCoupons(activeTab) {
        const { unusedCoupons = [], usedCoupons = [], expiredCoupons = [] } = this.data;
        let currentCoupons = [];
        if (activeTab === 'unused') {
            currentCoupons = unusedCoupons;
        } else if (activeTab === 'used') {
            currentCoupons = usedCoupons;
        } else if (activeTab === 'expired') {
            currentCoupons = expiredCoupons;
        }
        this.setData({
            currentCoupons: currentCoupons
        });
    },

    // 获取优惠券显示文本
    getCouponDisplayText(coupon) {
        if (coupon.coupon_type === 'discount') {
            return `满${coupon.min_purchase_amount}减${coupon.discount_amount}`;
        } else if (coupon.coupon_type === 'percentage') {
            const rate = Math.round(coupon.discount_rate * 100);
            return `${rate}折优惠`;
        } else if (coupon.coupon_type === 'cash') {
            return `${coupon.discount_amount}元现金券`;
        }
        return coupon.name;
    },

    // 使用优惠券
    useCoupon(e) {
        const couponId = e.currentTarget.dataset.id;
        wx.showModal({
            title: '使用优惠券',
            content: '确定要使用这张优惠券吗？',
            success: (res) => {
                if (res.confirm) {
                    // 这里可以跳转到商品页面或订单页面
                    wx.showToast({
                        title: '优惠券已使用',
                        icon: 'success'
                    });
                }
            }
        });
    }
});
