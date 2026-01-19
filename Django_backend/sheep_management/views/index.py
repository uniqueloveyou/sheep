"""首页视图"""
from django.shortcuts import render
from ..models import Sheep, Breeder, GrowthRecord, FeedingRecord, VaccinationHistory, User


def index(request):
    """首页 - 显示所有模块的统计信息"""
    context = {
        'sheep_count': Sheep.objects.count(),
        'breeder_count': Breeder.objects.count(),
        'growth_record_count': GrowthRecord.objects.count(),
        'feeding_record_count': FeedingRecord.objects.count(),
        'vaccination_count': VaccinationHistory.objects.count(),
        'user_count': User.objects.count(),
    }
    return render(request, 'sheep_management/index.html', context)

