// 引入API工具
const API = require('../../utils/api.js');

Page({
    data: {
        cartItems: [],
        totalPrice: 0
    },

    onShow: function () {
        if (typeof this.getTabBar === 'function' && this.getTabBar()) {
            const tabBar = this.getTabBar();
            tabBar.initTabBar();
            const index = tabBar.data.list.findIndex(item => item.pagePath === "/pages/cart/index");
            if (index > -1) {
                tabBar.setData({ selected: index });
            }
        }
        this.loadCartItems();
    },

    loadCartItems: function () {
        const that = this;
        const token = wx.getStorageSync('token');

        // 如果已登录，从服务器加载
        if (token) {
            wx.showLoading({
                title: '加载中...',
                mask: true
            });

            API.getCart(token)
                .then((res) => {
                    wx.hideLoading();
                    console.log('[购物车] 从服务器加载:', res);

                    if (Array.isArray(res)) {
                        // 格式化数据
                        const cartItems = res.map(item => {
                            const sheep = item.sheep || {};
                            return {
                                id: item.sheep_id || sheep.id || item.id,
                                cart_item_id: item.id, // 购物车记录ID，用于删除
                                sheep: sheep,
                                gender: sheep.gender || '',
                                weight: sheep.weight || 0,
                                height: sheep.height || 0,
                                length: sheep.length || 0,
                                quantity: item.quantity || 1,
                                price: item.price || 0,
                                total_price: item.total_price || (item.price * (item.quantity || 1)) || 0
                            };
                        });

                        // 同步到本地存储（作为备用）
                        wx.setStorageSync('cartItems', cartItems);

                        const totalPrice = cartItems.reduce((sum, item) => sum + (item.total_price || item.price || 0), 0);
                        that.setData({ cartItems, totalPrice });
                    } else {
                        // 如果服务器返回格式不对，使用本地存储
                        that.loadFromLocal();
                    }
                })
                .catch((error) => {
                    wx.hideLoading();
                    console.warn('[购物车] 从服务器加载失败，使用本地存储:', error);
                    // 降级到本地存储
                    that.loadFromLocal();
                });
        } else {
            // 未登录，使用本地存储
            this.loadFromLocal();
        }
    },

    // 从本地存储加载购物车
    loadFromLocal: function () {
        let cartItems = wx.getStorageSync('cartItems') || [];
        console.log('[购物车] 从本地加载:', cartItems);

        // 更新每个商品的价格为体重的十倍
        cartItems.forEach(item => {
            if (!item.price && item.weight) {
                item.price = (Number(item.weight) * 10) || 0;
            }
            item.total_price = (item.price || 0) * (item.quantity || 1);
        });

        const totalPrice = cartItems.reduce((sum, item) => sum + (item.total_price || item.price || 0), 0);
        this.setData({ cartItems, totalPrice });
    },

    deleteItem: function (e) {
        const that = this;
        const cartItemId = e.currentTarget.dataset.cartItemId; // 购物车记录ID
        const itemId = e.currentTarget.dataset.id; // 羊只ID
        const token = wx.getStorageSync('token');

        // 如果已登录且有购物车记录ID，从服务器删除
        if (token && cartItemId) {
            wx.showLoading({
                title: '删除中...',
                mask: true
            });

            API.removeFromCart(token, cartItemId)
                .then((res) => {
                    wx.hideLoading();
                    console.log('[购物车] 删除成功:', res);

                    // 同时更新本地存储
                    let cartItems = wx.getStorageSync('cartItems') || [];
                    cartItems = cartItems.filter(item => item.id != itemId && item.cart_item_id != cartItemId);
                    wx.setStorageSync('cartItems', cartItems);

                    that.loadCartItems(); // 重新加载
                    wx.showToast({
                        title: '已删除',
                        icon: 'success',
                        duration: 2000
                    });
                })
                .catch((error) => {
                    wx.hideLoading();
                    console.error('[购物车] 删除失败:', error);

                    // 降级处理：只删除本地存储
                    let cartItems = wx.getStorageSync('cartItems') || [];
                    cartItems = cartItems.filter(item => item.id != itemId);
                    wx.setStorageSync('cartItems', cartItems);
                    that.loadCartItems();

                    wx.showToast({
                        title: '已删除（离线模式）',
                        icon: 'success',
                        duration: 2000
                    });
                });
        } else {
            // 未登录或没有记录ID，只删除本地存储
            let cartItems = wx.getStorageSync('cartItems') || [];
            cartItems = cartItems.filter(item => item.id !== itemId);
            wx.setStorageSync('cartItems', cartItems);
            this.loadCartItems();
            wx.showToast({
                title: '已删除',
                icon: 'success',
                duration: 2000
            });
        }
    },

    viewOrderDetail: function (e) {
        const itemId = e.currentTarget.dataset.id;
        wx.navigateTo({
            url: `/pages/goodsdetail/goodsdetail?id=${itemId}` // 使用反引号
        });
    },

    checkout: function () {
        wx.showToast({
            title: '结算成功',
            icon: 'success',
            duration: 2000
        });
        wx.removeStorageSync('cartItems');
        this.setData({ cartItems: [], totalPrice: 0 });
    }
});
