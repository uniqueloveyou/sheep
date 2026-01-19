"""养殖户管理视图"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from ..models import Breeder, Sheep


def breeder_list(request):
    """养殖户列表"""
    search = request.GET.get('search', '')
    # 使用annotate统计每个养殖户的实际羊只数量
    breeder_list = Breeder.objects.annotate(actual_sheep_count=Count('sheep_list'))
    
    if search:
        breeder_list = breeder_list.filter(
            Q(name__icontains=search) | Q(phone__icontains=search) | Q(sheep_id__icontains=search)
        )
    
    context = {'breeder_list': breeder_list, 'search': search}
    return render(request, 'sheep_management/breeder/list.html', context)


def breeder_detail(request, pk):
    """养殖户详情"""
    breeder = get_object_or_404(Breeder, pk=pk)
    # 获取该养殖户的所有羊只
    sheep_list = Sheep.objects.filter(breeder=breeder).order_by('id')
    # 统计实际数量
    actual_sheep_count = sheep_list.count()
    # 统计性别分布
    actual_female_count = sheep_list.filter(gender__in=['母', '雌性', 'female']).count()
    actual_male_count = sheep_list.filter(gender__in=['公', '雄性', 'male']).count()
    
    context = {
        'breeder': breeder,
        'sheep_list': sheep_list,
        'actual_sheep_count': actual_sheep_count,
        'actual_female_count': actual_female_count,
        'actual_male_count': actual_male_count,
    }
    return render(request, 'sheep_management/breeder/detail.html', context)


def breeder_create(request):
    """创建养殖户"""
    if request.method == 'POST':
        breeder = Breeder.objects.create(
            name=request.POST.get('name'),
            gender=request.POST.get('gender'),
            phone=request.POST.get('phone'),
            sheep_count=int(request.POST.get('sheep_count')),
            sheep_id=request.POST.get('sheep_id'),
            female_count=int(request.POST.get('female_count')),
            male_count=int(request.POST.get('male_count')),
        )
        messages.success(request, '养殖户创建成功！')
        return redirect('breeder_detail', pk=breeder.pk)
    return render(request, 'sheep_management/breeder/form.html', {'title': '创建养殖户'})


def breeder_edit(request, pk):
    """编辑养殖户"""
    breeder = get_object_or_404(Breeder, pk=pk)
    if request.method == 'POST':
        breeder.name = request.POST.get('name')
        breeder.gender = request.POST.get('gender')
        breeder.phone = request.POST.get('phone')
        breeder.sheep_count = int(request.POST.get('sheep_count'))
        breeder.sheep_id = request.POST.get('sheep_id')
        breeder.female_count = int(request.POST.get('female_count'))
        breeder.male_count = int(request.POST.get('male_count'))
        breeder.save()
        messages.success(request, '养殖户信息更新成功！')
        return redirect('breeder_detail', pk=breeder.pk)
    return render(request, 'sheep_management/breeder/form.html', {'breeder': breeder, 'title': '编辑养殖户'})


def breeder_delete(request, pk):
    """删除养殖户"""
    breeder = get_object_or_404(Breeder, pk=pk)
    if request.method == 'POST':
        breeder.delete()
        messages.success(request, '养殖户删除成功！')
        return redirect('breeder_list')
    return render(request, 'sheep_management/breeder/confirm_delete.html', {'breeder': breeder})

