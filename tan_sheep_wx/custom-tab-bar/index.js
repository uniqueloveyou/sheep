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

            // 提取用户信息以判断角色
            const userInfoMap = wx.getStorageSync('apiUserInfoMap');
            const role = (userInfoMap && userInfoMap.base) ? userInfoMap.base.role : 0;
            const isVerified = (userInfoMap && userInfoMap.base) ? userInfoMap.base.is_verified : false;

            // 如果是养殖户 (role === 1 且 is_verified === true，或者直接根据 role 判断，依您的后台逻辑定)
            // 这里假定 role === 1 或 2 就可以看“我的羊”
            // 根据您的要求：名字是"我的羊之类的，就是查询自己的羊信息的"
            if (role === 1 && isVerified) {
                // 插入在首页和购物车之间（索引 1 的位置）
                baseList.splice(1, 0, {
                    pagePath: "/pages/my/adopt/adopt", // 暂用查看领养的页面替代，您可以后续修改真实页面
                    text: "我的羊",
                    iconPath: "/icons/_sheep.png", // 注意：您需要添加此图标文件
                    selectedIconPath: "/icons/sheep.png" // 注意：您需要添加此图标文件
                });
            }

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
