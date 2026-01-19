"""羊只管理视图"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from ..models import Sheep


def sheep_list(request):
    """羊只列表"""
    search = request.GET.get('search', '')
    sheep_list = Sheep.objects.all()
    
    if search:
        sheep_list = sheep_list.filter(
            Q(id__icontains=search) | Q(gender__icontains=search)
        )
    
    context = {'sheep_list': sheep_list, 'search': search}
    return render(request, 'sheep_management/sheep/list.html', context)


def sheep_detail(request, pk):
    """羊只详情"""
    sheep = get_object_or_404(Sheep, pk=pk)
    growth_records = sheep.growth_records.all().order_by('-record_date')
    feeding_records = sheep.feeding_records.all().order_by('-start_date')
    vaccination_records = sheep.vaccination_records.all().order_by('-vaccination_date')
    
    context = {
        'sheep': sheep,
        'growth_records': growth_records,
        'feeding_records': feeding_records,
        'vaccination_records': vaccination_records,
    }
    return render(request, 'sheep_management/sheep/detail.html', context)


def sheep_create(request):
    """创建羊只"""
    if request.method == 'POST':
        sheep = Sheep.objects.create(
            gender=request.POST.get('gender'),
            weight=float(request.POST.get('weight')),
            height=float(request.POST.get('height')),
            length=float(request.POST.get('length')),
        )
        messages.success(request, '羊只创建成功！')
        return redirect('sheep_detail', pk=sheep.pk)
    return render(request, 'sheep_management/sheep/form.html', {'title': '创建羊只'})


def sheep_edit(request, pk):
    """编辑羊只"""
    sheep = get_object_or_404(Sheep, pk=pk)
    if request.method == 'POST':
        sheep.gender = request.POST.get('gender')
        sheep.weight = float(request.POST.get('weight'))
        sheep.height = float(request.POST.get('height'))
        sheep.length = float(request.POST.get('length'))
        sheep.save()
        messages.success(request, '羊只信息更新成功！')
        return redirect('sheep_detail', pk=sheep.pk)
    return render(request, 'sheep_management/sheep/form.html', {'sheep': sheep, 'title': '编辑羊只'})


def sheep_delete(request, pk):
    """删除羊只"""
    sheep = get_object_or_404(Sheep, pk=pk)
    if request.method == 'POST':
        sheep.delete()
        messages.success(request, '羊只删除成功！')
        return redirect('sheep_list')
    return render(request, 'sheep_management/sheep/confirm_delete.html', {'sheep': sheep})

