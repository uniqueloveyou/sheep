"""用户管理视图"""
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from ..models import User


def user_list(request):
    """用户列表"""
    search = request.GET.get('search', '')
    user_list = User.objects.all()
    
    if search:
        user_list = user_list.filter(
            Q(username__icontains=search) | Q(nickname__icontains=search) | Q(openid__icontains=search) | Q(mobile__icontains=search)
        )
    
    context = {'user_list': user_list, 'search': search}
    return render(request, 'sheep_management/user/list.html', context)


def user_detail(request, pk):
    """用户详情"""
    user = get_object_or_404(User, pk=pk)
    context = {'user': user}
    return render(request, 'sheep_management/user/detail.html', context)

