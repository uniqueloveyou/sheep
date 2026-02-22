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
            // 每次页面显示都重新初始化，防止角色切换后未更新
            this.initTabBar();
        }
    },

    methods: {
        initTabBar() {
            // 基础菜单
            const baseList = [
                {
                    pagePath: "/pages/index/index",
                    text: "首页",
                    iconPath: "/icons/_home.png",
                    selectedIconPath: "/icons/home.png"
                },
                {
                    pagePath: "/pages/cart/index",
                    text: "购物车",
                    iconPath: "/icons/_cart.png",
                    selectedIconPath: "/icons/cart.png"
                },
                {
                    pagePath: "/pages/my/index",
                    text: "我的",
                    iconPath: "/icons/_my.png",
                    selectedIconPath: "/icons/my.png"
                }
            ];

            // “我的羊”对所有用户可见，插入在首页和购物车之间（索引 1 的位置）
            baseList.splice(1, 0, {
                pagePath: "/pages/my/adopt/adopt",
                text: "我的羊",
                iconPath: "/icons/_sheep.png",
                selectedIconPath: "/icons/sheep.png"
            });

            this.setData({
                list: baseList
            });
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
