"""Smart farm monitor center pages."""
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@login_required
def smart_farm(request):
    """Monitor center page for admin and breeder."""
    user = request.user
    if user.role not in (1, 2):
        return HttpResponseForbidden("您没有权限访问该页面")
    context = {
        "user": user,
        "is_admin": user.role == 2,
        "is_breeder": user.role == 1,
        "initial_breeder_id": request.GET.get("breeder_id", ""),
    }
    return render(request, "sheep_management/smart_farm.html", context)


@csrf_exempt
def api_monitor_breeders(request):
    from ..api.monitor_api import api_monitor_breeders as api_func
    return api_func(request)


@csrf_exempt
def api_monitor_devices(request):
    from ..api.monitor_api import api_monitor_devices as api_func
    return api_func(request)


@csrf_exempt
def api_monitor_create(request):
    from ..api.monitor_api import api_monitor_create as api_func
    return api_func(request)


@csrf_exempt
def api_monitor_update(request, device_id):
    from ..api.monitor_api import api_monitor_update as api_func
    return api_func(request, device_id=device_id)


@csrf_exempt
def api_monitor_delete(request, device_id):
    from ..api.monitor_api import api_monitor_delete as api_func
    return api_func(request, device_id=device_id)
