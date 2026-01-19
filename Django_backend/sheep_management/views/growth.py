"""生长记录管理视图"""
from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import Sheep, GrowthRecord


def growth_record_list(request):
    """生长记录列表"""
    sheep_id = request.GET.get('sheep_id', '')
    growth_records = GrowthRecord.objects.all().select_related('sheep')
    
    if sheep_id:
        growth_records = growth_records.filter(sheep_id=sheep_id)
    
    context = {'growth_records': growth_records, 'sheep_id': sheep_id}
    return render(request, 'sheep_management/growth/list.html', context)


def growth_record_create(request):
    """创建生长记录"""
    if request.method == 'POST':
        growth_record = GrowthRecord.objects.create(
            sheep_id=int(request.POST.get('sheep_id')),
            record_date=request.POST.get('record_date'),
            weight=float(request.POST.get('weight')),
            height=float(request.POST.get('height')),
            length=float(request.POST.get('length')),
        )
        messages.success(request, '生长记录创建成功！')
        return redirect('growth_record_list')
    
    sheep_list = Sheep.objects.all()
    return render(request, 'sheep_management/growth/form.html', {'title': '创建生长记录', 'sheep_list': sheep_list})

