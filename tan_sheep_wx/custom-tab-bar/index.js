const TRACE_UNREAD_STORAGE_KEY = 'mySheepTraceUnreadCount';

function getMySheepBadgeText() {
    const unreadCount = parseInt(wx.getStorageSync(TRACE_UNREAD_STORAGE_KEY) || 0, 10);
    if (!unreadCount || unreadCount < 1) {
        return '';
    }
    return unreadCount > 99 ? '99+' : String(unreadCount);
}

Component({
    data: {
        selected: 0,
        color: "#999",
        selectedColor: "#FF5700",
        backgroundColor: "#fafafa",
        list: []
    },

    attached() {
        this.initTabBar();
    },

    pageLifetimes: {
        show() {
            this.initTabBar();
        }
    },

    methods: {
        initTabBar() {
            const mySheepBadge = getMySheepBadgeText();
            const baseList = [
                {
                    pagePath: "/pages/index/index",
                    text: "首页",
                    iconPath: "/icons/_home.png",
                    selectedIconPath: "/icons/home.png",
                    badge: ""
                },
                {
                    pagePath: "/pages/cart/index",
                    text: "购物车",
                    iconPath: "/icons/_cart.png",
                    selectedIconPath: "/icons/cart.png",
                    badge: ""
                },
                {
                    pagePath: "/pages/my/index",
                    text: "我的",
                    iconPath: "/icons/_my.png",
                    selectedIconPath: "/icons/my.png",
                    badge: ""
                }
            ];

            baseList.splice(1, 0, {
                pagePath: "/pages/my/adopt/adopt",
                text: "我的羊",
                iconPath: "/icons/_sheep.png",
                selectedIconPath: "/icons/sheep.png",
                badge: mySheepBadge
            });

            this.setData({
                list: baseList
            });
        },

        refreshBadges() {
            this.initTabBar();
        },

        switchTab(e) {
            const data = e.currentTarget.dataset;
            const url = data.path;
            wx.switchTab({ url });
            this.setData({
                selected: data.index
            });
        }
    }
})
