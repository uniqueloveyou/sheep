"""羊只管理视图"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ..models import Sheep, GrowthRecord, FeedingRecord, VaccinationHistory, VaccineType, EnvironmentAlert


def sheep_list(request):
    """羊只列表 - 带多条件筛选"""
    # 获取筛选参数
    search = request.GET.get('search', '')
    health_status = request.GET.get('health_status', '')
    gender = request.GET.get('gender', '')
    
    # 基础查询 - 只显示当前用户的羊只
    sheep_list = Sheep.objects.filter(owner=request.user)
    
    # 搜索ID或耳标号
    if search:
        sheep_list = sheep_list.filter(
            Q(id__icontains=search) | Q(ear_tag__icontains=search)
        )
    
    # 按健康状态筛选
    if health_status:
        sheep_list = sheep_list.filter(health_status=health_status)
    
    # 按性别筛选
    if gender:
        sheep_list = sheep_list.filter(gender=int(gender))
    
    # 获取筛选选项
    health_choices = Sheep.HEALTH_STATUS_CHOICES
    gender_choices = Sheep.GENDER_CHOICES
    
    context = {
        'sheep_list': sheep_list,
        'search': search,
        'health_status': health_status,
        'gender': gender,
        'health_choices': health_choices,
        'gender_choices': gender_choices,
    }
    return render(request, 'sheep_management/sheep/list.html', context)


def sheep_detail(request, pk):
    """羊只详情"""
    sheep = get_object_or_404(Sheep, pk=pk)
    growth_records = sheep.growth_records.all().order_by('-record_date')
    feeding_records = sheep.feeding_records.all().order_by('-start_date')
    vaccination_records = sheep.vaccination_records.all().order_by('-vaccination_date')
    vaccines = VaccineType.objects.all()
    
    context = {
        'sheep': sheep,
        'growth_records': growth_records,
        'feeding_records': feeding_records,
        'vaccination_records': vaccination_records,
        'vaccines': vaccines,
    }
    return render(request, 'sheep_management/sheep/detail.html', context)


@login_required
def sheep_add_growth(request, pk):
    """添加生长记录"""
    sheep = get_object_or_404(Sheep, pk=pk)
    if request.method == 'POST':
        GrowthRecord.objects.create(
            sheep=sheep,
            record_date=request.POST.get('record_date'),
            weight=float(request.POST.get('weight')),
            height=float(request.POST.get('height')),
            length=float(request.POST.get('length')),
        )
        messages.success(request, '生长记录添加成功！')
    return redirect('sheep_detail', pk=sheep.pk)


@login_required
def sheep_delete_growth(request, pk, record_id):
    """删除生长记录"""
    sheep = get_object_or_404(Sheep, pk=pk)
    record = get_object_or_404(GrowthRecord, pk=record_id, sheep=sheep)
    if request.method == 'POST':
        record.delete()
        messages.success(request, '生长记录删除成功！')
    return redirect('sheep_detail', pk=sheep.pk)


@login_required
def sheep_add_feeding(request, pk):
    """添加喂养记录"""
    sheep = get_object_or_404(Sheep, pk=pk)
    if request.method == 'POST':
        FeedingRecord.objects.create(
            sheep=sheep,
            feed_type=request.POST.get('feed_type'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date') or None,
            amount=float(request.POST.get('amount')),
            unit=request.POST.get('unit'),
        )
        messages.success(request, '喂养记录添加成功！')
    return redirect('sheep_detail', pk=sheep.pk)


@login_required
def sheep_delete_feeding(request, pk, record_id):
    """删除喂养记录"""
    sheep = get_object_or_404(Sheep, pk=pk)
    record = get_object_or_404(FeedingRecord, pk=record_id, sheep=sheep)
    if request.method == 'POST':
        record.delete()
        messages.success(request, '喂养记录删除成功！')
    return redirect('sheep_detail', pk=sheep.pk)


@login_required
def sheep_add_vaccination(request, pk):
    """添加疫苗接种记录"""
    sheep = get_object_or_404(Sheep, pk=pk)
    if request.method == 'POST':
        vaccine = get_object_or_404(VaccineType, pk=request.POST.get('vaccine_id'))
        VaccinationHistory.objects.create(
            sheep=sheep,
            vaccine=vaccine,
            vaccination_date=request.POST.get('vaccination_date'),
            expiry_date=request.POST.get('expiry_date'),
            dosage=float(request.POST.get('dosage')),
            administered_by=request.POST.get('administered_by'),
        )
        messages.success(request, '疫苗接种记录添加成功！')
    return redirect('sheep_detail', pk=sheep.pk)


@login_required
def sheep_delete_vaccination(request, pk, record_id):
    """删除疫苗接种记录"""
    sheep = get_object_or_404(Sheep, pk=pk)
    record = get_object_or_404(VaccinationHistory, pk=record_id, sheep=sheep)
    if request.method == 'POST':
        record.delete()
        messages.success(request, '疫苗接种记录删除成功！')
    return redirect('sheep_detail', pk=sheep.pk)


@login_required
def sheep_create(request):
    """创建羊只"""
    if request.method == 'POST':
        sheep = Sheep.objects.create(
            gender=int(request.POST.get('gender')),
            health_status=request.POST.get('health_status', '健康'),
            weight=float(request.POST.get('weight')),
            height=float(request.POST.get('height')),
            length=float(request.POST.get('length')),
            birth_date=request.POST.get('birth_date') or None,
            owner=request.user,
        )
        messages.success(request, '羊只创建成功！')
        return redirect('sheep_detail', pk=sheep.pk)
    context = {
        'title': '创建羊只',
        'health_choices': Sheep.HEALTH_STATUS_CHOICES,
    }
    return render(request, 'sheep_management/sheep/form.html', context)

@login_required
def sheep_edit(request, pk):
    """编辑羊只"""
    sheep = get_object_or_404(Sheep, pk=pk)
    if request.method == 'POST':
        sheep.gender = int(request.POST.get('gender'))
        sheep.health_status = request.POST.get('health_status', '健康')
        sheep.weight = float(request.POST.get('weight'))
        sheep.height = float(request.POST.get('height'))
        sheep.length = float(request.POST.get('length'))
        sheep.birth_date = request.POST.get('birth_date') or None
        sheep.save()
        messages.success(request, '羊只信息更新成功！')
        return redirect('sheep_detail', pk=sheep.pk)
    context = {
        'sheep': sheep,
        'title': '编辑羊只',
        'health_choices': Sheep.HEALTH_STATUS_CHOICES,
    }
    return render(request, 'sheep_management/sheep/form.html', context)

@login_required
def sheep_delete(request, pk):
    """删除羊只"""
    sheep = get_object_or_404(Sheep, pk=pk)
    if request.method == 'POST':
        sheep.delete()
        messages.success(request, '羊只删除成功！')
        return redirect('sheep_list')
    return render(request, 'sheep_management/sheep/confirm_delete.html', {'sheep': sheep})


@login_required
def resolve_alert(request, pk):
    """标记环境预警为已处理"""
    alert = get_object_or_404(EnvironmentAlert, pk=pk, owner=request.user)
    if request.method == 'POST':
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save()
        messages.success(request, '预警已标记为已处理！')
    return redirect('index')
