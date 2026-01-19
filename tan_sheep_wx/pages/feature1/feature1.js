Page({
    data: {
        categories: ["雄性", "雌性"],
        selectedCategory: '',
        weightRanges: ["40-50 kg", "50-55 kg", "55-60 kg"],
        selectedWeight: '', 
        heightRanges: ["55-60 cm", "60-65 cm", "65-70 cm", "70-75 cm", "75-80 cm", "80-85 cm", "85-90 cm", "90-95 cm", "95-100 cm"],
        selectedHeight: '', 
        lengthRanges: ["55-60 cm", "60-65 cm", "65-70 cm", "70-75 cm", "75-80 cm", "80-85 cm", "85-90 cm", "90-95 cm", "95-100 cm"],
        sheepList: [],
        selectedLength: ''
    }, 
    onGenderChange: function (e) {
        this.setData({
            selectedCategory: this.data.categories[e.detail.value]
        });
    },
    onWeightChange: function (e) {
        this.setData({
            selectedWeight: this.data.weightRanges[e.detail.value]
        });
    },
    onHeightChange: function (e) {
        this.setData({
            selectedHeight: this.data.heightRanges[e.detail.value]
        });
    },
    onLengthChange: function (e) {
        this.setData({
            selectedLength: this.data.lengthRanges[e.detail.value]
        });
    },
    formSubmit: function (e) {
        var that = this;
        
        // 检查是否选择了所有条件
        if (that.data.selectedCategory === '请选择' || 
            that.data.selectedWeight === '请选择体重区间' ||
            that.data.selectedHeight === '请选择体高区间' ||
            that.data.selectedLength === '请选择体长区间') {
            wx.showToast({
                title: '请选择完整的搜索条件',
                icon: 'none',
                duration: 2000
            });
            return;
        }
        
        wx.showLoading({
            title: '搜索中...',
            mask: true
        });
        
        // 使用统一的API工具
        const API = require('../../utils/api.js');
        
        API.request('/search_sheep', 'GET', {
            gender: that.data.selectedCategory,
            weight: that.data.selectedWeight,
            height: that.data.selectedHeight,
            length: that.data.selectedLength
        }).then((res) => {
            wx.hideLoading();
            that.setData({
                sheepList: res || []
            });
            
            if (!res || res.length === 0) {
                wx.showToast({
                    title: '未找到符合条件的羊只',
                    icon: 'none',
                    duration: 2000
                });
            } else {
                wx.showToast({
                    title: `找到 ${res.length} 只羊`,
                    icon: 'success',
                    duration: 1500
                });
            }
        }).catch((error) => {
            wx.hideLoading();
            console.error('Request failed:', error);
            
            // 更详细的错误提示
            let errorMsg = '网络请求失败';
            if (error.message) {
                if (error.message.includes('CONNECTION_REFUSED')) {
                    errorMsg = '后端服务未启动\n请启动Django后端服务（端口8000）';
                } else if (error.message.includes('timeout')) {
                    errorMsg = '请求超时，请检查网络';
                }
            }
            
            wx.showModal({
                title: '连接失败',
                content: errorMsg + '\n\n请检查：\n1. Django后端服务是否启动\n2. 端口8000是否被占用\n3. 网络连接是否正常',
                confirmText: '知道了',
                showCancel: false
            });
        });
    },
    formReset: function () {
        this.setData({
            selectedCategory: '请选择',
            selectedWeight: '请选择体重区间',
            selectedHeight: '请选择体高区间',
            selectedLength: '请选择体长区间'
        });
    },
    viewSheepDetail: function (event) {
        const sheepId = event.currentTarget.dataset.id;
        const url = `/pages/feature1/customize/customize?id=${sheepId}`;
        wx.navigateTo({
            url: url
        });
    },
  
    onLoad: function (options) {
        const gender = decodeURIComponent(options.gender);
        this.setData({
            genderDetail: gender
        });
    },

    onReady() {

    },

    onShow() {

    },
    onHide() {

    },


    onUnload() {

    },

 
    onPullDownRefresh() {

    },
    onReachBottom() {

    },

    onShareAppMessage() {

    }
})