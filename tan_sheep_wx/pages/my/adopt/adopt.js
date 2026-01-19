// adopt.js
Page({
    data: {
      adoptionList: []
    },
  
    onShow: function() {
      const adoptionList = wx.getStorageSync('adoptionList') || [];
      this.setData({
        adoptionList: adoptionList
      });
    },
  
    deleteAdoption: function(e) {
      const index = e.currentTarget.dataset.index;
      let adoptionList = this.data.adoptionList;
      adoptionList.splice(index, 1);

      wx.setStorageSync('adoptionList', adoptionList);
      this.setData({
        adoptionList: adoptionList
      });
    }
  });
  