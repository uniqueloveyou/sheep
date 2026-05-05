"""订单管理视图"""
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from ..models import Order, OrderItem
from ..permissions import login_required, ROLE_ADMIN, ROLE_BREEDER
from ..services.commerce_service import CommerceService, CommerceError


ACTIVE_ORDER_STATUS_ALIASES = {'paid', 'adopting', 'ready_to_ship'}
CARE_FEE_EDITABLE_STATUSES = {'paid', 'adopting', 'ready_to_ship'}


def _attach_order_finance(order):
    """Attach display-only finance fields used by backend templates."""
    care_fee_amount = order.care_fee_amount or Decimal('0')
    order.final_amount_display = (order.total_amount or Decimal('0')) + care_fee_amount
    order.care_fee_display = care_fee_amount
    order.has_care_fee = care_fee_amount > 0
    return order


@login_required
def order_list(request):
    """订单列表——管理员看全部，养殖户只看自己名下羊只的订单"""
    user = request.user
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '').strip()
    page_number = request.GET.get('page', 1)

    if user.role == ROLE_ADMIN:
        orders = Order.objects.all()
    else:
        # 养殖户：订单里含有自己旗下羊只的才显示
        orders = Order.objects.filter(items__sheep__owner=user).distinct()

    if status_filter == 'paid':
        orders = orders.filter(status__in=['paid', 'adopting', 'ready_to_ship'])
    elif status_filter:
        orders = orders.filter(status=status_filter)

    if search:
        orders = orders.filter(
            Q(order_no__icontains=search) |
            Q(user__nickname__icontains=search) |
            Q(user__username__icontains=search) |
            Q(user__mobile__icontains=search)
        )

    orders = orders.order_by('-created_at')
    paginator = Paginator(orders, 10)
    page_obj = paginator.get_page(page_number)
    for order in page_obj.object_list:
        _attach_order_finance(order)

    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_string = query_params.urlencode()

    # 各状态计数
    if user.role == ROLE_ADMIN:
        base_qs = Order.objects.all()
    else:
        base_qs = Order.objects.filter(items__sheep__owner=user).distinct()

    stats = {
        'total':     base_qs.count(),
        'pending':   base_qs.filter(status='pending').count(),
        'paid':      base_qs.filter(status__in=['paid', 'adopting', 'ready_to_ship']).count(),
        'settlement_pending': base_qs.filter(status='settlement_pending').count(),
        'awaiting_delivery': base_qs.filter(status='awaiting_delivery').count(),
        'shipping':  base_qs.filter(status='shipping').count(),
        'completed': base_qs.filter(status='completed').count(),
        'cancelled': base_qs.filter(status='cancelled').count(),
    }

    context = {
        'orders': page_obj.object_list,
        'page_obj': page_obj,
        'query_string': query_string,
        'stats': stats,
        'status_filter': status_filter,
        'search': search,
        'is_admin': user.role == ROLE_ADMIN,
    }
    return render(request, 'sheep_management/order/list.html', context)


@login_required
def order_detail(request, pk):
    """订单详情——养殖户只能看自己的"""
    user = request.user
    if user.role == ROLE_ADMIN:
        order = get_object_or_404(Order, pk=pk)
    else:
        order = get_object_or_404(Order, pk=pk, items__sheep__owner=user)
    _attach_order_finance(order)

    context = {'order': order, 'is_admin': user.role == ROLE_ADMIN}
    return render(request, 'sheep_management/order/detail.html', context)


@login_required
def order_update_status(request, pk):
    """更新订单状态——养殖户只能操作自己的订单"""
    from django.utils import timezone
    user = request.user

    if user.role == ROLE_ADMIN:
        order = get_object_or_404(Order, pk=pk)
    else:
        order = get_object_or_404(Order, pk=pk, items__sheep__owner=user)

    if request.method == 'POST':
        status = request.POST.get('status')
        if status == 'adopting' and order.status in ACTIVE_ORDER_STATUS_ALIASES:
            status = order.status
        logistics_info = {
            'delivery_method': request.POST.get('delivery_method', 'logistics'),
            'logistics_company': request.POST.get('logistics_company', ''),
            'logistics_tracking_number': request.POST.get('logistics_tracking_number', ''),
            'offline_delivery_location': request.POST.get('offline_delivery_location', ''),
            'offline_delivery_note': request.POST.get('offline_delivery_note', ''),
        }
        try:
            if order.status in CARE_FEE_EDITABLE_STATUSES:
                fee_raw = request.POST.get('daily_care_fee', '')
                if fee_raw != '':
                    try:
                        daily_care_fee = Decimal(str(fee_raw)).quantize(Decimal('0.01'))
                    except (InvalidOperation, TypeError, ValueError) as exc:
                        raise CommerceError('请输入正确的订单基础照料费。') from exc
                    if daily_care_fee < 0:
                        raise CommerceError('订单基础照料费不能小于 0。')
                    order.daily_care_fee = daily_care_fee
            if user.role != ROLE_ADMIN:
                owner_ids = set(order.items.values_list('sheep__owner_id', flat=True))
                if owner_ids != {user.id}:
                    raise CommerceError('该订单包含其他养殖户的羊只，请由管理员处理')
            CommerceService._validate_order_transition(order, status, logistics_info)
        except CommerceError as e:
            messages.error(request, e.message)
            return redirect('order_update_status', pk=order.pk)

        order.status = status

        if status == 'shipping':
            delivery_method = logistics_info['delivery_method']
            order.delivery_method = delivery_method
            if delivery_method == 'logistics':
                order.logistics_company = logistics_info['logistics_company'].strip()
                order.logistics_tracking_number = logistics_info['logistics_tracking_number'].strip()
                order.offline_delivery_location = ''
                order.offline_delivery_note = ''
            else:
                order.logistics_company = ''
                order.logistics_tracking_number = ''
                order.offline_delivery_location = logistics_info['offline_delivery_location'].strip()
                order.offline_delivery_note = logistics_info['offline_delivery_note'].strip()
            order.shipping_date = timezone.now()
        elif status == 'completed' and not order.delivery_date:
            order.delivery_date = timezone.now()

        order.save()
        messages.success(request, '订单状态更新成功！')
        return redirect('order_detail', pk=order.pk)

    adopting_status_value = order.status if order.status in ACTIVE_ORDER_STATUS_ALIASES else 'adopting'
    context = {
        'order': order,
        'is_admin': user.role == ROLE_ADMIN,
        'adopting_status_value': adopting_status_value,
        'can_edit_daily_care_fee': order.status in CARE_FEE_EDITABLE_STATUSES,
    }
    return render(request, 'sheep_management/order/update_status.html', context)
