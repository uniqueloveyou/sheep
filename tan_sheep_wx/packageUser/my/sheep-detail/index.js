const API = require('../../../utils/api.js');

const TRACE_SEEN_STORAGE_KEY = 'mySheepTraceSeenMap';
const TRACE_UNREAD_STORAGE_KEY = 'mySheepTraceUnreadCount';

Page({
    data: {
        sheepId: null,
        sheepDetail: null,
        vaccineRecords: [],
        growthRecords: [],
        feedingRecords: [],
        loading: true
    },

    onLoad: function (options) {
        if (options.id) {
            const sheepId = options.id;
            this.setData({ sheepId: sheepId });

            if (options.latest_trace_date) {
                this.markTraceAsRead(sheepId, decodeURIComponent(options.latest_trace_date));
            }

            this.loadSheepData(sheepId);
        } else {
            wx.showToast({ title: '参数错误', icon: 'none' });
            setTimeout(() => wx.navigateBack(), 1500);
        }
    },

    markTraceAsRead: function (sheepId, latestTraceDate) {
        if (!sheepId || !latestTraceDate) {
            return;
        }

        const seenMap = wx.getStorageSync(TRACE_SEEN_STORAGE_KEY) || {};
        const currentSeenDate = seenMap[String(sheepId)] || '';

        if (!currentSeenDate || latestTraceDate > currentSeenDate) {
            seenMap[String(sheepId)] = latestTraceDate;
            wx.setStorageSync(TRACE_SEEN_STORAGE_KEY, seenMap);

            const unreadCount = parseInt(wx.getStorageSync(TRACE_UNREAD_STORAGE_KEY) || 0, 10);
            wx.setStorageSync(TRACE_UNREAD_STORAGE_KEY, unreadCount > 0 ? unreadCount - 1 : 0);
        }
    },

    loadSheepData: function (sheepId) {
        this.setData({ loading: true });

        Promise.all([
            API.request(`/api/sheep/${sheepId}`, 'GET'),
            API.request(`/api/growth/sheep/${sheepId}`, 'GET').catch((err) => {
                console.error('获取溯源记录失败:', err);
                return null;
            }),
            API.request(`/vaccine_records/${sheepId}`, 'GET').catch((err) => {
                console.error('获取疫苗失败:', err);
                return [];
            })
        ])
            .then(([res, traceRes, vaccineRes]) => {
                if (res && res.id) {
                    const detail = {
                        id: res.id,
                        ear_tag: res.ear_tag || '暂无耳标',
                        gender: res.gender || '未知',
                        weight: res.weight ? parseFloat(res.weight).toFixed(1) : '0.0',
                        height: res.height ? parseFloat(res.height).toFixed(1) : '0.0',
                        length: res.length ? parseFloat(res.length).toFixed(1) : '0.0',
                        birth_date: res.birth_date ? res.birth_date.split('T')[0] : '暂无出生日期',
                        status: res.status_display || '健康养殖中',
                        farm_name: res.farm_name || '宁夏盐池核心牧场',
                        breeder_name: res.breeder_name || '官方推荐养殖户',
                        owner_id: res.owner_id,
                        qr_code: (res.qr_code && !res.qr_code.startsWith('http'))
                            ? (API.API_BASE_URL + res.qr_code)
                            : (res.qr_code || ''),
                        image: (res.image && !res.image.startsWith('http'))
                            ? (API.API_BASE_URL + res.image)
                            : (res.image || '')
                    };
                    const growthRecords = traceRes && Array.isArray(traceRes.growth_records)
                        ? traceRes.growth_records
                        : [];
                    const feedingRecords = traceRes && Array.isArray(traceRes.feeding_records)
                        ? traceRes.feeding_records
                        : [];
                    const vaccinationRecords = Array.isArray(vaccineRes)
                        ? vaccineRes
                        : [];

                    this.setData({
                        sheepDetail: detail,
                        growthRecords: growthRecords,
                        feedingRecords: feedingRecords,
                        vaccineRecords: vaccinationRecords.map(record => ({
                            ...record,
                            VaccinationDate: record.VaccinationDate ? record.VaccinationDate.split('T')[0] : ''
                        })),
                        loading: false
                    });
                } else {
                    throw new Error('羊只不存在');
                }
            })
            .catch((error) => {
                console.error('获取羊详情失败:', error);
                this.setData({ loading: false });
                wx.showToast({ title: '加载失败', icon: 'none' });
            });
    },

    previewQRCode: function () {
        const qrCodeUrl = this.data.sheepDetail && this.data.sheepDetail.qr_code;
        if (qrCodeUrl) {
            wx.previewImage({
                urls: [qrCodeUrl]
            });
        }
    },

    previewSheepImage: function () {
        const imageUrl = this.data.sheepDetail && this.data.sheepDetail.image;
        if (imageUrl) {
            wx.previewImage({
                urls: [imageUrl]
            });
        }
    },

    viewMonitor: function () {
        wx.showToast({ title: '牧场监控接入中...', icon: 'none' });
    },

    viewBreederDetail: function (e) {
        const breederId = e.currentTarget.dataset.id;
        if (breederId) {
            wx.navigateTo({
                url: `/pages/breeder/my1/my1?id=${breederId}`
            });
        } else {
            wx.showToast({ title: '暂无养殖户信息', icon: 'none' });
        }
    }
});
