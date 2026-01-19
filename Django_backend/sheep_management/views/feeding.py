"""喂养记录管理视图"""
from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import Sheep, FeedingRecord


def feeding_record_list(request):
    """喂养记录列表"""
    sheep_id = request.GET.get('sheep_id', '')
    feeding_records = FeedingRecord.objects.all().select_related('sheep')
    
    if sheep_id:
        feeding_records = feeding_records.filter(sheep_id=sheep_id)
    
    context = {'feeding_records': feeding_records, 'sheep_id': sheep_id}
    return render(request, 'sheep_management/feeding/list.html', context)


def feeding_record_create(request):
    """创建喂养记录"""
    if request.method == 'POST':
        feeding_record = FeedingRecord.objects.create(
            sheep_id=int(request.POST.get('sheep_id')),
            feed_type=request.POST.get('feed_type'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date') or None,
            amount=float(request.POST.get('amount')),
            unit=request.POST.get('unit'),
        )
        messages.success(request, '喂养记录创建成功！')
        return redirect('feeding_record_list')
    
    sheep_list = Sheep.objects.all()
    return render(request, 'sheep_management/feeding/form.html', {'title': '创建喂养记录', 'sheep_list': sheep_list})

