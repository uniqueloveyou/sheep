"""羊只管理视图"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from ..models import Sheep, GrowthRecord, FeedingRecord, VaccinationHistory, VaccineType, EnvironmentAlert, User, OrderItem
from ..permissions import ROLE_ADMIN, ROLE_BREEDER
from ..services.sheep_service import SheepService


ADOPTED_ORDER_STATUSES = [
    'paid',
    'adopting',
    'ready_to_ship',
    'settlement_pending',
    'awaiting_delivery',
    'shipping',
    'completed',
]


@login_required
def sheep_list(request):
    """羊只列表 - 带多条件筛选"""
    is_admin = request.user.role == ROLE_ADMIN
    page_number = request.GET.get('page', 1)
    adoption_tab = request.GET.get('adoption_tab', 'available')
    if adoption_tab not in {'available', 'adopted'}:
        adoption_tab = 'available'
    
    # 获取筛选参数
    search = request.GET.get('search', '')
    health_status = request.GET.get('health_status', '')
    gender = request.GET.get('gender', '')
    owner_filter = request.GET.get('owner', '')
    
    # 基础查询 - 管理员看全部，养殖户只看自己的
    if is_admin:
        sheep_list = Sheep.objects.select_related('owner').all()
    else:
        sheep_list = Sheep.objects.filter(owner=request.user)
    
    # 搜索ID或耳标号
    if search:
        sheep_list = sheep_list.filter(
            Q(id__icontains=search) | Q(ear_tag__icontains=search)
        )
    
    # 管理员按养殖户筛选
    if is_admin and owner_filter:
        sheep_list = sheep_list.filter(owner_id=int(owner_filter))
    
    # 按健康状态筛选
    if health_status:
        sheep_list = sheep_list.filter(health_status=health_status)
    
    # 按性别筛选
    if gender:
        sheep_list = sheep_list.filter(gender=int(gender))

    adopted_sheep_ids = list(
        OrderItem.objects.filter(
            sheep__in=sheep_list,
            order__status__in=ADOPTED_ORDER_STATUSES,
        ).values_list('sheep_id', flat=True).distinct()
    )
    available_count = sheep_list.exclude(id__in=adopted_sheep_ids).count()
    adopted_count = sheep_list.filter(id__in=adopted_sheep_ids).count()

    if adoption_tab == 'adopted':
        sheep_list = sheep_list.filter(id__in=adopted_sheep_ids)
    else:
        sheep_list = sheep_list.exclude(id__in=adopted_sheep_ids)

    # 默认按最新羊只排序，并做分页
    sheep_queryset = sheep_list.order_by('-id')
    paginator = Paginator(sheep_queryset, 10)
    page_obj = paginator.get_page(page_number)
    current_sheep_list = list(page_obj.object_list)

    # 批量查询当前页每只羊的认养订单信息
    sheep_ids = [s.id for s in current_sheep_list]
    adoption_map = {}
    for oi in OrderItem.objects.filter(
        sheep_id__in=sheep_ids,
        order__status__in=ADOPTED_ORDER_STATUSES
    ).select_related('order__user', 'order').order_by('-order__created_at'):
        adoption_map.setdefault(oi.sheep_id, oi.order)

    for s in current_sheep_list:
        s.adoption_order = adoption_map.get(s.id)
        s.adopter = s.adoption_order.user if s.adoption_order else None
        s.uses_default_care_fee = s.daily_care_fee is None

    # 获取筛选选项
    health_choices = Sheep.HEALTH_STATUS_CHOICES
    gender_choices = Sheep.GENDER_CHOICES
    
    # 管理员需要养殖户列表（用于筛选和创建）
    breeders = []
    if is_admin:
        breeders = User.objects.filter(role=ROLE_BREEDER, is_verified=True).order_by('id')
    
    context = {
        'sheep_list': current_sheep_list,
        'page_obj': page_obj,
        'search': search,
        'health_status': health_status,
        'gender': gender,
        'owner_filter': owner_filter,
        'adoption_tab': adoption_tab,
        'available_count': available_count,
        'adopted_count': adopted_count,
        'table_colspan': 12 if is_admin and adoption_tab == 'available' else (11 if adoption_tab == 'available' else 12),
        'health_choices': health_choices,
        'gender_choices': gender_choices,
        'is_admin': is_admin,
        'breeders': breeders,
    }
    return render(request, 'sheep_management/sheep/list.html', context)


@login_required
def sheep_batch_delete(request):
    """批量删除可领养羊只"""
    if request.method != 'POST':
        return redirect('sheep_list')

    sheep_ids = request.POST.getlist('sheep_ids')
    next_url = request.POST.get('next') or ''
    redirect_url = next_url if next_url.startswith('/') and not next_url.startswith('//') else None

    if not sheep_ids:
        messages.warning(request, '请先选择要删除的羊只')
        return redirect(redirect_url or 'sheep_list')

    is_admin = request.user.role == ROLE_ADMIN
    sheep_queryset = Sheep.objects.filter(pk__in=sheep_ids)
    if not is_admin:
        sheep_queryset = sheep_queryset.filter(owner=request.user)

    adopted_ids = set(
        OrderItem.objects.filter(
            sheep__in=sheep_queryset,
            order__status__in=ADOPTED_ORDER_STATUSES,
        ).values_list('sheep_id', flat=True)
    )
    deletable_queryset = sheep_queryset.exclude(id__in=adopted_ids)
    deleted_count = deletable_queryset.count()
    skipped_count = len(set(str(sid) for sid in sheep_ids)) - deleted_count

    if deleted_count:
        deletable_queryset.delete()
        messages.success(request, f'已删除 {deleted_count} 只可领养羊只')
    if skipped_count:
        messages.warning(request, f'{skipped_count} 只羊因已领养、无权限或不存在，未删除')
    if not deleted_count and not skipped_count:
        messages.warning(request, '没有可删除的羊只')

    return redirect(redirect_url or 'sheep_list')


@login_required
def sheep_detail(request, pk):
    """羊只详情"""
    sheep = get_object_or_404(Sheep, pk=pk)
    is_admin = request.user.role == ROLE_ADMIN
    
    # 权限检查：养殖户只能看自己的羊
    if not is_admin and sheep.owner != request.user:
        messages.error(request, '无权查看该羊只信息')
        return redirect('sheep_list')

    if not sheep.qr_code:
        from ..utils import generate_qr_code
        generate_qr_code(sheep)

    from ..utils import get_r2_public_url
    qr_code_url = get_r2_public_url(sheep.qr_code.name) if sheep.qr_code else ''
    
    growth_records = sheep.growth_records.all().order_by('-record_date')
    feeding_records = sheep.feeding_records.all().order_by('-feed_date')
    vaccination_records = sheep.vaccination_records.all().order_by('-vaccination_date')
    vaccines = VaccineType.objects.all()
    
    context = {
        'sheep': sheep,
        'growth_records': growth_records,
        'feeding_records': feeding_records,
        'vaccination_records': vaccination_records,
        'vaccines': vaccines,
        'is_admin': is_admin,
        'qr_code_url': qr_code_url,
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
            feed_date=request.POST.get('feed_date'),
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
    is_admin = request.user.role == ROLE_ADMIN
    
    if request.method == 'POST':
        # 确定所属养殖户
        if is_admin:
            owner_id = request.POST.get('owner')
            if not owner_id:
                messages.error(request, '请选择所属养殖户')
                return redirect('sheep_create')
            owner = get_object_or_404(User, pk=int(owner_id), role=ROLE_BREEDER)
        else:
            owner = request.user
        
        sheep = Sheep.objects.create(
            gender=int(request.POST.get('gender')),
            health_status=request.POST.get('health_status', '健康'),
            weight=float(request.POST.get('weight')),
            height=float(request.POST.get('height')),
            length=float(request.POST.get('length')),
            birth_date=request.POST.get('birth_date') or None,
            price=float(request.POST.get('price', 0)),
            daily_care_fee=request.POST.get('daily_care_fee') or None,
            owner=owner,
        )
        if request.FILES.get('image'):
            sheep.image = request.FILES['image']
            sheep.save()
        messages.success(request, f'羊只创建成功！耳标号：{sheep.ear_tag}')
        return redirect('sheep_detail', pk=sheep.pk)
    
    # 管理员需要养殖户列表
    breeders = []
    if is_admin:
        breeders = User.objects.filter(role=ROLE_BREEDER, is_verified=True).order_by('id')
    
    context = {
        'title': '创建羊只',
        'health_choices': Sheep.HEALTH_STATUS_CHOICES,
        'is_admin': is_admin,
        'breeders': breeders,
    }
    return render(request, 'sheep_management/sheep/form.html', context)

@login_required
def sheep_edit(request, pk):
    """编辑羊只"""
    sheep = get_object_or_404(Sheep, pk=pk)
    is_admin = request.user.role == ROLE_ADMIN
    
    # 权限检查：养殖户只能编辑自己的羊
    if not is_admin and sheep.owner != request.user:
        messages.error(request, '无权编辑该羊只信息')
        return redirect('sheep_list')
    
    if request.method == 'POST':
        # 管理员可以转移羊只归属
        if is_admin:
            new_owner_id = request.POST.get('owner')
            if new_owner_id:
                sheep.owner = get_object_or_404(User, pk=int(new_owner_id), role=ROLE_BREEDER)
        
        sheep.gender = int(request.POST.get('gender'))
        sheep.health_status = request.POST.get('health_status', '健康')
        sheep.weight = float(request.POST.get('weight'))
        sheep.height = float(request.POST.get('height'))
        sheep.length = float(request.POST.get('length'))
        sheep.birth_date = request.POST.get('birth_date') or None
        sheep.price = float(request.POST.get('price', 0))
        sheep.daily_care_fee = request.POST.get('daily_care_fee') or None
        if request.FILES.get('image'):
            sheep.image = request.FILES['image']
        sheep.save()
        SheepService.sync_editable_orders_daily_care_fee(sheep)
        messages.success(request, '羊只信息更新成功！')
        return redirect('sheep_detail', pk=sheep.pk)
    
    # 管理员需要养殖户列表
    breeders = []
    if is_admin:
        breeders = User.objects.filter(role=ROLE_BREEDER, is_verified=True).order_by('id')
    
    context = {
        'sheep': sheep,
        'title': '编辑羊只',
        'health_choices': Sheep.HEALTH_STATUS_CHOICES,
        'is_admin': is_admin,
        'breeders': breeders,
    }
    return render(request, 'sheep_management/sheep/form.html', context)

@login_required
def sheep_delete(request, pk):
    """删除羊只"""
    sheep = get_object_or_404(Sheep, pk=pk)
    is_admin = request.user.role == ROLE_ADMIN
    
    # 权限检查：养殖户只能删除自己的羊
    if not is_admin and sheep.owner != request.user:
        messages.error(request, '无权删除该羊只')
        return redirect('sheep_list')

    if OrderItem.objects.filter(sheep=sheep, order__status__in=ADOPTED_ORDER_STATUSES).exists():
        messages.error(request, '该羊只已被领养，不能删除；请在已领养羊只中查看订单和交付状态。')
        return redirect('sheep_list')
    
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
