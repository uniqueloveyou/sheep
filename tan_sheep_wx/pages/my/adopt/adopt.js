// adopt.js
Page({
  data: {
    adoptionList: []
  },

  onShow: function () {
    const adoptionList = wx.getStorageSync('adoptionList') || [];
    this.setData({
      adoptionList: adoptionList
    });

    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      const tabBar = this.getTabBar();
      tabBar.initTabBar();
      const index = tabBar.data.list.findIndex(item => item.pagePath === "/pages/my/adopt/adopt");
      if (index > -1) {
        tabBar.setData({ selected: index });
      }
    }
  },

  deleteAdoption: function (e) {
    const index = e.currentTarget.dataset.index;
    let adoptionList = this.data.adoptionList;
    adoptionList.splice(index, 1);

    wx.setStorageSync('adoptionList', adoptionList);
    this.setData({
      adoptionList: adoptionList
    });
  }
});
