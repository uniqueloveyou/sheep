"""养殖户管理视图（养殖户 = role=1 的 User）"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from ..models import User, Sheep


def breeder_list(request):
    """养殖户列表"""
    search = request.GET.get('search', '')
    breeder_list = User.objects.filter(role=1).annotate(actual_sheep_count=Count('sheep_list'))

    if search:
        breeder_list = breeder_list.filter(
            Q(nickname__icontains=search) | Q(mobile__icontains=search) | Q(username__icontains=search)
        )

    context = {'breeder_list': breeder_list, 'search': search}
    return render(request, 'sheep_management/breeder/list.html', context)


def breeder_detail(request, pk):
    """养殖户详情"""
    breeder = get_object_or_404(User, pk=pk, role=1)
    sheep_list = Sheep.objects.filter(owner=breeder).order_by('id')
    actual_sheep_count = sheep_list.count()
    actual_female_count = sheep_list.filter(gender=0).count()
    actual_male_count = sheep_list.filter(gender=1).count()

    context = {
        'breeder': breeder,
        'sheep_list': sheep_list,
        'actual_sheep_count': actual_sheep_count,
        'actual_female_count': actual_female_count,
        'actual_male_count': actual_male_count,
    }
    return render(request, 'sheep_management/breeder/detail.html', context)


def breeder_create(request):
    """创建养殖户（创建 role=1 的用户）"""
    if request.method == 'POST':
        breeder = User.objects.create(
            username=request.POST.get('username'),
            nickname=request.POST.get('nickname', ''),
            mobile=request.POST.get('mobile', ''),
            role=1,
        )
        messages.success(request, '养殖户创建成功！')
        return redirect('breeder_detail', pk=breeder.pk)
    return render(request, 'sheep_management/breeder/form.html', {'title': '创建养殖户'})


def breeder_edit(request, pk):
    """编辑养殖户"""
    breeder = get_object_or_404(User, pk=pk, role=1)
    if request.method == 'POST':
        breeder.username = request.POST.get('username', breeder.username)
        breeder.nickname = request.POST.get('nickname', breeder.nickname)
        breeder.mobile = request.POST.get('mobile', breeder.mobile)
        breeder.save()
        messages.success(request, '养殖户信息更新成功！')
        return redirect('breeder_detail', pk=breeder.pk)
    return render(request, 'sheep_management/breeder/form.html', {'breeder': breeder, 'title': '编辑养殖户'})


def breeder_delete(request, pk):
    """删除养殖户"""
    breeder = get_object_or_404(User, pk=pk, role=1)
    if request.method == 'POST':
        breeder.delete()
        messages.success(request, '养殖户删除成功！')
        return redirect('breeder_list')
    return render(request, 'sheep_management/breeder/confirm_delete.html', {'breeder': breeder})
