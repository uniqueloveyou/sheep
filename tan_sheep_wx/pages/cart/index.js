// 引入API工具
const API = require('../../utils/api.js');

Page({
    data: {
        cartItems: [],
        totalPrice: 0,
        selectedCount: 0,
        allSelected: false,
        hasCartItems: false,
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

                    // 后端返回 { code: 0, data: [...] } 格式
                    const cartData = res.data || res;
                    const items = Array.isArray(cartData) ? cartData : [];

                    // 格式化数据
                    const baseUrl = API.API_BASE_URL;
                    const cartItems = items.map(item => {
                        const sheep = item.sheep || {};
                        const unitPrice = item.price || sheep.price || 0;
                        const qty = item.quantity || 1;
                        // 转换图片为绝对 URL
                        let imageUrl = sheep.image || '';
                        if (imageUrl && !imageUrl.startsWith('http://') && !imageUrl.startsWith('https://')) {
                            imageUrl = baseUrl + imageUrl;
                        }
                        const rawDailyCareFee = item.daily_care_fee !== undefined && item.daily_care_fee !== null
                            ? item.daily_care_fee
                            : sheep.daily_care_fee;
                        const dailyCareFee = parseFloat(rawDailyCareFee);
                        return {
                            id: sheep.id || item.sheep_id || item.id,
                            cart_item_id: item.id, // 购物车记录ID，用于删除
                            sheep: { ...sheep, image: imageUrl },
                            gender: sheep.gender || '',
                            weight: sheep.weight || 0,
                            height: sheep.height || 0,
                            length: sheep.length || 0,
                            quantity: qty,
                            price: unitPrice,
                            daily_care_fee: isNaN(dailyCareFee) ? 10 : dailyCareFee,
                            dailyCareFeeText: isNaN(dailyCareFee) ? '10.00' : dailyCareFee.toFixed(2),
                            total_price: unitPrice * qty,
                            selected: true  // 默认全选
                        };
                    });

                    if (cartItems.length === 0) {
                        wx.removeStorageSync('checkoutItems');
                    }
                    that.setData({
                        cartItems,
                        ...that._getSelectionState(cartItems)
                    });
                })
                .catch((error) => {
                    wx.hideLoading();
                    console.error('[购物车] 从服务器加载失败:', error);
                    wx.removeStorageSync('checkoutItems');
                    that.setData(that._getEmptyCartState());
                    wx.showToast({ title: '加载失败', icon: 'none' });
                });
        } else {
            // 未登录，提示登录
            wx.removeStorageSync('checkoutItems');
            this.setData(this._getEmptyCartState());
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

        this.setData({
            cartItems,
            ...this._getSelectionState(cartItems)
        });
    },

    deleteItem: function (e) {
        const that = this;
        const cartItemId = e.currentTarget.dataset.cartItemId; // 购物车记录ID
        const token = wx.getStorageSync('token');

        if (!token || !cartItemId) {
            wx.showToast({ title: '操作失败', icon: 'none' });
            return;
        }

        wx.showModal({
            title: '确认删除',
            content: '确认从购物车中移除吗？',
            success: function (res) {
                if (res.confirm) {
                    wx.showLoading({ title: '删除中...', mask: true });

                    API.removeFromCart(token, cartItemId)
                        .then((res) => {
                            wx.hideLoading();
                            console.log('[购物车] 删除成功:', res);
                            const remainingItems = (that.data.cartItems || []).filter(item => String(item.cart_item_id) !== String(cartItemId));
                            if (remainingItems.length === 0) {
                                wx.removeStorageSync('checkoutItems');
                            }
                            that.setData({
                                cartItems: remainingItems,
                                ...that._getSelectionState(remainingItems)
                            });
                            that.loadCartItems(); // 重新加载
                            wx.showToast({ title: '已删除', icon: 'success' });
                        })
                        .catch((error) => {
                            wx.hideLoading();
                            console.error('[购物车] 删除失败:', error);
                            wx.showToast({ title: '删除失败', icon: 'none' });
                        });
                }
            }
        });
    },

    // 单个商品切换选中状态
    toggleSelect: function (e) {
        const index = e.currentTarget.dataset.index;
        const cartItems = (this.data.cartItems || []).slice();
        if (!cartItems[index]) return;
        cartItems[index].selected = !cartItems[index].selected;
        this.setData({
            cartItems,
            ...this._getSelectionState(cartItems)
        });
    },

    // 全选 / 取消全选
    toggleSelectAll: function () {
        const allSelected = !this.data.allSelected;
        const cartItems = (this.data.cartItems || []).map(item => ({
            ...item,
            selected: allSelected
        }));
        this.setData({
            cartItems,
            ...this._getSelectionState(cartItems, allSelected)
        });
    },

    // 重新计算选中数量和总价
    _getSelectionState: function (cartItems, allSelectedOverride) {
        cartItems = cartItems || [];
        const selectedItems = cartItems.filter(item => item.selected);
        const totalPrice = selectedItems.reduce((sum, item) => sum + (item.total_price || 0), 0);
        const selectedCount = selectedItems.length;
        const allSelected = typeof allSelectedOverride === 'boolean'
            ? allSelectedOverride
            : (cartItems.length > 0 && selectedCount === cartItems.length);
        return {
            totalPrice,
            selectedCount,
            allSelected,
            hasCartItems: cartItems.length > 0
        };
    },

    _getEmptyCartState: function () {
        return {
            cartItems: [],
            totalPrice: 0,
            selectedCount: 0,
            allSelected: false,
            hasCartItems: false
        };
    },

    viewOrderDetail: function (e) {
        const itemId = e.currentTarget.dataset.id;
        wx.navigateTo({
            url: `/pages/goodsdetail/goodsdetail?id=${itemId}` // 使用反引号
        });
    },

    checkout: function () {
        const token = wx.getStorageSync('token');
        if (!token) { wx.showToast({ title: '请先登录', icon: 'none' }); return; }
        const selectedItems = (this.data.cartItems || []).filter(item => item.selected && item.cart_item_id);
        if (!this.data.hasCartItems || this.data.cartItems.length === 0) {
            wx.removeStorageSync('checkoutItems');
            wx.showToast({ title: '购物车为空', icon: 'none' });
            return;
        }
        if (selectedItems.length === 0) { wx.showToast({ title: '请先选择要结算的羊只', icon: 'none' }); return; }

        // 将选中商品存入缓存，跳转到订单确认页
        wx.setStorageSync('checkoutItems', selectedItems);
        wx.navigateTo({ url: '/packageOrder/cart/checkout' });
    },

    goToHistory: function () {
        wx.navigateTo({
            url: '/packageOrder/cart/history/index'
        });
    },

    goHome: function () {
        wx.switchTab({
            url: '/pages/index/index'
        });
    }
});

