"""
H5 公开溯源页面视图
URL: /trace/<sheep_id>/
无需登录，供扫码后在浏览器/微信中直接访问。
"""
from django.shortcuts import render, get_object_or_404

from ..models import Sheep, VaccinationHistory, GrowthRecord, FeedingRecord


def sheep_trace_h5(request, sheep_id):
    """渲染羊只溯源 H5 页面"""
    sheep = get_object_or_404(Sheep.objects.select_related('owner'), pk=sheep_id)

    # 疫苗接种记录
    vaccinations = list(
        VaccinationHistory.objects
        .filter(sheep=sheep)
        .select_related('vaccine')
        .order_by('-vaccination_date')
        .values(
            'vaccine__name', 'vaccination_date', 'expiry_date',
            'dosage', 'administered_by', 'notes'
        )
    )

    # 生长记录（最近 6 条，倒序展示）
    growth_records = list(
        GrowthRecord.objects
        .filter(sheep=sheep)
        .order_by('-record_date')[:6]
        .values('record_date', 'weight', 'height', 'length')
    )

    # 喂养记录（最近 10 条）
    feeding_records = list(
        FeedingRecord.objects
        .filter(sheep=sheep)
        .order_by('-feed_date')[:10]
        .values('feed_date', 'feed_type', 'amount', 'unit')
    )

    context = {
        'sheep': sheep,
        'vaccinations': vaccinations,
        'growth_records': growth_records,
        'feeding_records': feeding_records,
    }
    return render(request, 'sheep_management/sheep_trace.html', context)
