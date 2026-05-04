// pages/trace/detail.js
// 扫码后的溯源详情页：通过 sheep_id 拉取完整生命周期数据
const API = require('../../utils/api.js');
const RECORD_PAGE_SIZE = 10;

function paginate(list, page) {
    const safeList = Array.isArray(list) ? list : [];
    const totalPages = Math.max(1, Math.ceil(safeList.length / RECORD_PAGE_SIZE));
    const currentPage = Math.min(Math.max(parseInt(page || 1, 10), 1), totalPages);
    const start = (currentPage - 1) * RECORD_PAGE_SIZE;
    return {
        list: safeList.slice(start, start + RECORD_PAGE_SIZE),
        currentPage,
        totalPages
    };
}

Page({
    data: {
        sheepId: null,
        sheep: null,
        loading: true,
        error: null,
        vaccineExpanded: true,
        growthExpanded: true,
        feedExpanded: false,
        vaccinePage: 1,
        vaccineTotalPages: 1,
        growthPage: 1,
        growthTotalPages: 1,
        feedPage: 1,
        feedTotalPages: 1,
    },

    onLoad(options) {
        const sheepId = options.sheep_id || options.id;
        const earTag  = API.normalizeEarTag(options.ear_tag);
        if (sheepId) {
            this.setData({ sheepId });
            this.fetchBySheepId(sheepId);
        } else if (earTag) {
            this.fetchByEarTag(earTag);
        } else {
            this.setData({ loading: false, error: '缺少羊只标识参数' });
        }
    },

    fetchBySheepId(id) {
        wx.showLoading({ title: '溯源查询中', mask: true });
        API.request('/api/public/trace/' + id, 'GET')
            .then(res => {
                wx.hideLoading();
                if (res.code === 0) {
                    this.setSheepData(res.data);
                } else {
                    this.setData({ loading: false, error: res.msg || '查询失败' });
                }
            })
            .catch(err => {
                wx.hideLoading();
                const errorMessage = this._fmtError(err);
                wx.showToast({ title: errorMessage, icon: 'none', duration: 2000 });
                this.setData({ loading: false, error: errorMessage });
            });
    },

    fetchByEarTag(earTag) {
        if (!API.isValidEarTag(earTag)) {
            wx.showToast({ title: '输入格式有误，请重新输入', icon: 'none', duration: 2000 });
            this.setData({ loading: false, error: '输入格式有误，请重新输入' });
            return;
        }
        wx.showLoading({ title: '溯源查询中', mask: true });
        API.request('/api/sheep/trace?ear_tag=' + encodeURIComponent(earTag), 'GET')
            .then(res => {
                wx.hideLoading();
                const sheep = (res && res.id) ? res : (res && res.data ? res.data : null);
                if (sheep && sheep.id) {
                    this.fetchBySheepId(sheep.id);
                } else {
                    this.setData({ loading: false, error: '未找到该羊只信息' });
                }
            })
            .catch(err => {
                wx.hideLoading();
                const errorMessage = this._fmtError(err);
                wx.showToast({ title: errorMessage, icon: 'none', duration: 2000 });
                this.setData({ loading: false, error: errorMessage });
            });
    },

    setSheepData(sheep) {
        const nextSheep = Object.assign({}, sheep || {});
        const vaccine = paginate(nextSheep.vaccinations, this.data.vaccinePage);
        const growth = paginate(nextSheep.growth_records, this.data.growthPage);
        const feed = paginate(nextSheep.feeding_records, this.data.feedPage);

        nextSheep.paged_vaccinations = vaccine.list;
        nextSheep.paged_growth_records = growth.list;
        nextSheep.paged_feeding_records = feed.list;

        this.setData({
            sheep: nextSheep,
            vaccinePage: vaccine.currentPage,
            vaccineTotalPages: vaccine.totalPages,
            growthPage: growth.currentPage,
            growthTotalPages: growth.totalPages,
            feedPage: feed.currentPage,
            feedTotalPages: feed.totalPages,
            loading: false,
            error: null
        });
    },

    changeRecordPage(e) {
        const type = e.currentTarget.dataset.type;
        const direction = Number(e.currentTarget.dataset.direction || 0);
        const pageKey = `${type}Page`;
        const totalKey = `${type}TotalPages`;
        const nextPage = Math.min(
            Math.max((this.data[pageKey] || 1) + direction, 1),
            this.data[totalKey] || 1
        );
        if (nextPage === this.data[pageKey]) {
            return;
        }
        this.setData({ [pageKey]: nextPage });
        this.setSheepData(this.data.sheep);
    },

    toggleSection(e) {
        const key = e.currentTarget.dataset.key;
        this.setData({ [key]: !this.data[key] });
    },

    previewQRCode() {
        const url = this.data.sheep && this.data.sheep.qr_code;
        if (url) wx.previewImage({ urls: [url], current: url });
    },

    retry() {
        this.setData({ loading: true, error: null });
        if (this.data.sheepId) this.fetchBySheepId(this.data.sheepId);
    },

    goBack() { wx.navigateBack(); },

    _fmtError(err) {
        if (err && err.response && err.response.msg) return err.response.msg;
        if (!err) return '查询失败，请稍后重试。';
        if (err.statusCode === 404) return '未找到该羊只溯源信息，请检查二维码是否正确。';
        if (err.statusCode >= 500) return '服务器繁忙，请稍后再试。';
        if (err.errMsg && err.errMsg.indexOf('timeout') !== -1) return '网络请求超时，请检查网络连接。';
        return '查询失败，请稍后重试。';
    }
});
