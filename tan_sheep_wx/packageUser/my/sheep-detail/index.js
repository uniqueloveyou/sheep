const API = require('../../../utils/api.js');

const TRACE_SEEN_STORAGE_KEY = 'mySheepTraceSeenMap';
const TRACE_UNREAD_STORAGE_KEY = 'mySheepTraceUnreadCount';
const RECORD_PAGE_SIZE = 10;
const TRACE_TIMELINE_PREVIEW_SIZE = 6;

function normalizeDate(dateStr) {
    return String(dateStr || '').trim().slice(0, 10);
}

function buildAssetUrl(url) {
    if (!url) {
        return '';
    }
    if (url.startsWith('http://') || url.startsWith('https://')) {
        return url;
    }
    return API.API_BASE_URL + url;
}

function shouldMarkAsNew(recordDate, previousSeenDate, latestTraceDate) {
    const normalizedRecordDate = normalizeDate(recordDate);
    if (!normalizedRecordDate) {
        return false;
    }

    if (previousSeenDate) {
        return normalizedRecordDate > previousSeenDate;
    }

    if (latestTraceDate) {
        return normalizedRecordDate === latestTraceDate;
    }

    return false;
}

function buildDynamicItems(vaccineRecords, growthRecords, feedingRecords) {
    const items = [];

    vaccineRecords.forEach((record) => {
        if (!record.isNew) {
            return;
        }
        items.push({
            id: record.id,
            type: 'vaccination',
            typeLabel: '疫苗记录',
            date: record.displayDate,
            title: record.vaccineType || '疫苗接种',
            summary: record.expiryDate
                ? `接种于 ${record.displayDate}，有效期至 ${record.expiryDate}`
                : `接种于 ${record.displayDate}`,
            meta: `操作人 ${record.administeredBy || '未记录'} · 剂量 ${record.dosageText}`
        });
    });

    growthRecords.forEach((record) => {
        if (!record.isNew) {
            return;
        }
        items.push({
            id: record.id,
            type: 'growth',
            typeLabel: '生长记录',
            date: record.recordDate,
            title: '体征更新',
            summary: `体重 ${record.weightText} · 体高 ${record.heightText} · 体长 ${record.lengthText}`,
            meta: '已同步到成长档案'
        });
    });

    feedingRecords.forEach((record) => {
        if (!record.isNew) {
            return;
        }
        items.push({
            id: record.id,
            type: 'feeding',
            typeLabel: '喂养记录',
            date: record.feedDate,
            title: record.feedType || '日常喂养',
            summary: `投喂量 ${record.amountText}`,
            meta: '已同步到饲养档案'
        });
    });

    return items.sort((a, b) => String(b.date).localeCompare(String(a.date)));
}

function buildTraceTimelineItems(vaccineRecords, growthRecords, feedingRecords) {
    const items = [];

    vaccineRecords.forEach((record) => {
        items.push({
            id: record.id,
            type: 'vaccination',
            typeLabel: '疫苗',
            date: record.displayDate,
            sortDate: record.sortDate || record.displayDate,
            title: record.vaccineType || '疫苗接种',
            summary: record.expiryDate
                ? `有效期至 ${record.expiryDate}`
                : '已完成接种记录',
            meta: `操作人 ${record.administeredBy || '未记录'} · 剂量 ${record.dosageText}`,
            isNew: record.isNew
        });
    });

    growthRecords.forEach((record) => {
        items.push({
            id: record.id,
            type: 'growth',
            typeLabel: '生长',
            date: record.recordDate,
            sortDate: record.sortDate || record.recordDate,
            title: '体征更新',
            summary: `体重 ${record.weightText} · 体高 ${record.heightText} · 体长 ${record.lengthText}`,
            meta: '成长档案记录',
            isNew: record.isNew
        });
    });

    feedingRecords.forEach((record) => {
        items.push({
            id: record.id,
            type: 'feeding',
            typeLabel: '喂养',
            date: record.feedDate,
            sortDate: record.sortDate || record.feedDate,
            title: record.feedType || '日常喂养',
            summary: `投喂量 ${record.amountText}`,
            meta: '饲养档案记录',
            isNew: record.isNew
        });
    });

    return items.sort((a, b) => String(b.sortDate).localeCompare(String(a.sortDate)));
}

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
        sheepDetail: null,
        vaccineRecords: [],
        pagedVaccineRecords: [],
        vaccinePage: 1,
        vaccineTotalPages: 1,
        growthRecords: [],
        pagedGrowthRecords: [],
        growthPage: 1,
        growthTotalPages: 1,
        feedingRecords: [],
        pagedFeedingRecords: [],
        feedingPage: 1,
        feedingTotalPages: 1,
        traceDynamicItems: [],
        traceDynamicPreview: [],
        traceTimelineItems: [],
        traceTimelinePreview: [],
        traceTimelineExpanded: false,
        traceTimelineCanToggle: false,
        traceSummaryText: '',
        traceStats: {
            vaccines: 0,
            growth: 0,
            feeding: 0,
            total: 0
        },
        latestTraceDate: '',
        previousSeenDate: '',
        newTraceCount: 0,
        loading: true
    },

    onLoad: function (options) {
        if (!options.id) {
            wx.showToast({ title: '参数错误', icon: 'none' });
            setTimeout(() => wx.navigateBack(), 1500);
            return;
        }

        const sheepId = options.id;
        const latestTraceDate = normalizeDate(decodeURIComponent(options.latest_trace_date || ''));
        const previousSeenDate = this.getTraceSeenDate(sheepId);

        this.setData({
            sheepId: sheepId,
            latestTraceDate: latestTraceDate,
            previousSeenDate: previousSeenDate
        });

        if (latestTraceDate) {
            this.markTraceAsRead(sheepId, latestTraceDate);
        }

        this.loadSheepData(sheepId);
    },

    getTraceSeenDate: function (sheepId) {
        const seenMap = wx.getStorageSync(TRACE_SEEN_STORAGE_KEY) || {};
        return normalizeDate(seenMap[String(sheepId)] || '');
    },

    markTraceAsRead: function (sheepId, latestTraceDate) {
        if (!sheepId || !latestTraceDate) {
            return;
        }

        const seenMap = wx.getStorageSync(TRACE_SEEN_STORAGE_KEY) || {};
        const currentSeenDate = normalizeDate(seenMap[String(sheepId)] || '');

        if (!currentSeenDate || latestTraceDate > currentSeenDate) {
            seenMap[String(sheepId)] = latestTraceDate;
            wx.setStorageSync(TRACE_SEEN_STORAGE_KEY, seenMap);

            const unreadCount = parseInt(wx.getStorageSync(TRACE_UNREAD_STORAGE_KEY) || 0, 10);
            wx.setStorageSync(TRACE_UNREAD_STORAGE_KEY, unreadCount > 0 ? unreadCount - 1 : 0);
        }
    },

    loadSheepData: function (sheepId) {
        const previousSeenDate = this.data.previousSeenDate;
        const latestTraceDate = this.data.latestTraceDate;

        this.setData({ loading: true });

        API.request(`/api/public/trace/${sheepId}`, 'GET')
            .then((res) => {
                const payload = res && res.data ? res.data : null;
                if (!payload || !payload.id) {
                    throw new Error('羊只不存在');
                }

                const vaccineRecords = (payload.vaccinations || []).map((record, index) => {
                    const displayDate = normalizeDate(record.vaccination_date);
                    const dosageValue = record.dosage !== undefined && record.dosage !== null
                        ? record.dosage
                        : '';

                    return {
                        id: `vaccination-${index}-${displayDate}`,
                        vaccineType: record.vaccine_type || '疫苗接种',
                        displayDate: displayDate || '未记录日期',
                        sortDate: displayDate,
                        expiryDate: normalizeDate(record.expiry_date),
                        administeredBy: record.administered_by || '',
                        dosageText: dosageValue !== '' ? `${dosageValue}ml` : '未记录',
                        notes: record.notes || '',
                        isNew: shouldMarkAsNew(displayDate, previousSeenDate, latestTraceDate)
                    };
                });

                const growthRecords = (payload.growth_records || []).map((record, index) => {
                    const recordDate = normalizeDate(record.record_date);
                    return {
                        id: `growth-${index}-${recordDate}`,
                        recordDate: recordDate || '未记录日期',
                        sortDate: recordDate,
                        weightText: `${record.weight || 0}kg`,
                        heightText: `${record.height || 0}cm`,
                        lengthText: `${record.length || 0}cm`,
                        isNew: shouldMarkAsNew(recordDate, previousSeenDate, latestTraceDate)
                    };
                });

                const feedingRecords = (payload.feeding_records || []).map((record, index) => {
                    const feedDate = normalizeDate(record.feed_date);
                    const amount = record.amount !== undefined && record.amount !== null ? record.amount : 0;
                    const unit = record.unit || '';
                    return {
                        id: `feeding-${index}-${feedDate}`,
                        feedDate: feedDate || '未记录日期',
                        sortDate: feedDate,
                        feedType: record.feed_type || '日常喂养',
                        amountText: `${amount}${unit}`,
                        isNew: shouldMarkAsNew(feedDate, previousSeenDate, latestTraceDate)
                    };
                });

                const traceDynamicItems = buildDynamicItems(vaccineRecords, growthRecords, feedingRecords);
                const traceTimelineItems = buildTraceTimelineItems(vaccineRecords, growthRecords, feedingRecords);
                const newTraceCount = traceTimelineItems.filter((item) => item.isNew).length;
                const latestTimelineDate = traceTimelineItems.length > 0 ? traceTimelineItems[0].date : '';
                const displayLatestTraceDate = latestTimelineDate || latestTraceDate;
                const traceSummaryText = newTraceCount > 0
                    ? `本次新增 ${newTraceCount} 条溯源记录，完整时间线已更新`
                    : (traceTimelineItems.length > 0
                        ? `已汇总 ${traceTimelineItems.length} 条养殖记录，最近更新于 ${displayLatestTraceDate}`
                        : '当前还没有溯源记录');

                const vaccinePageData = paginate(vaccineRecords, 1);
                const growthPageData = paginate(growthRecords, 1);
                const feedingPageData = paginate(feedingRecords, 1);

                this.setData({
                    sheepDetail: {
                        id: payload.id,
                        ear_tag: payload.ear_tag || '暂无耳标',
                        gender: payload.gender || '未知',
                        weight: payload.weight ? parseFloat(payload.weight).toFixed(1) : '0.0',
                        height: payload.height ? parseFloat(payload.height).toFixed(1) : '0.0',
                        length: payload.length ? parseFloat(payload.length).toFixed(1) : '0.0',
                        birth_date: payload.birth_date || '暂无出生日期',
                        age_display: payload.age_display || '未设置',
                        status: payload.health_status || '健康养殖中',
                        farm_name: payload.farm_name || '宁夏盐池核心牧场',
                        breeder_name: payload.breeder && payload.breeder.name ? payload.breeder.name : '官方推荐养殖户',
                        breeder_phone: payload.breeder && payload.breeder.phone ? payload.breeder.phone : '',
                        owner_id: payload.breeder && payload.breeder.id ? payload.breeder.id : '',
                        qr_code: buildAssetUrl(payload.qr_code),
                        image: buildAssetUrl(payload.image),
                    },
                    vaccineRecords: vaccineRecords,
                    pagedVaccineRecords: vaccinePageData.list,
                    vaccinePage: vaccinePageData.currentPage,
                    vaccineTotalPages: vaccinePageData.totalPages,
                    growthRecords: growthRecords,
                    pagedGrowthRecords: growthPageData.list,
                    growthPage: growthPageData.currentPage,
                    growthTotalPages: growthPageData.totalPages,
                    feedingRecords: feedingRecords,
                    pagedFeedingRecords: feedingPageData.list,
                    feedingPage: feedingPageData.currentPage,
                    feedingTotalPages: feedingPageData.totalPages,
                    traceDynamicItems: traceDynamicItems,
                    traceDynamicPreview: traceDynamicItems.slice(0, 3),
                    traceTimelineItems: traceTimelineItems,
                    traceTimelinePreview: traceTimelineItems.slice(0, TRACE_TIMELINE_PREVIEW_SIZE),
                    traceTimelineExpanded: false,
                    traceTimelineCanToggle: traceTimelineItems.length > TRACE_TIMELINE_PREVIEW_SIZE,
                    traceSummaryText: traceSummaryText,
                    traceStats: {
                        vaccines: vaccineRecords.length,
                        growth: growthRecords.length,
                        feeding: feedingRecords.length,
                        total: vaccineRecords.length + growthRecords.length + feedingRecords.length
                    },
                    latestTraceDate: displayLatestTraceDate,
                    newTraceCount: newTraceCount,
                    loading: false
                });
            })
            .catch((error) => {
                console.error('获取羊详情失败:', error);
                this.setData({ loading: false });
                wx.showToast({ title: '加载失败', icon: 'none' });
            });
    },

    toggleTraceTimeline: function () {
        const nextExpanded = !this.data.traceTimelineExpanded;
        this.setData({
            traceTimelineExpanded: nextExpanded,
            traceTimelinePreview: nextExpanded
                ? this.data.traceTimelineItems
                : this.data.traceTimelineItems.slice(0, TRACE_TIMELINE_PREVIEW_SIZE)
        });
    },

    changeRecordPage: function (e) {
        const type = e.currentTarget.dataset.type;
        const direction = Number(e.currentTarget.dataset.direction || 0);
        const config = {
            vaccine: {
                listKey: 'vaccineRecords',
                pagedKey: 'pagedVaccineRecords',
                pageKey: 'vaccinePage',
                totalKey: 'vaccineTotalPages'
            },
            growth: {
                listKey: 'growthRecords',
                pagedKey: 'pagedGrowthRecords',
                pageKey: 'growthPage',
                totalKey: 'growthTotalPages'
            },
            feeding: {
                listKey: 'feedingRecords',
                pagedKey: 'pagedFeedingRecords',
                pageKey: 'feedingPage',
                totalKey: 'feedingTotalPages'
            }
        }[type];

        if (!config) {
            return;
        }

        const nextPage = Math.min(
            Math.max((this.data[config.pageKey] || 1) + direction, 1),
            this.data[config.totalKey] || 1
        );
        if (nextPage === this.data[config.pageKey]) {
            return;
        }

        const pageData = paginate(this.data[config.listKey], nextPage);
        this.setData({
            [config.pagedKey]: pageData.list,
            [config.pageKey]: pageData.currentPage,
            [config.totalKey]: pageData.totalPages
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
