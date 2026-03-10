"""Monitor APIs for admin and breeder."""
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..services.user_service import UserService, UserError
from ..services.monitor_service import MonitorService, MonitorError


def _success(data=None, msg="success"):
    return JsonResponse({"code": 0, "msg": msg, "data": data}, status=200)


def _error(message, code=400, http_status=400):
    return JsonResponse({"code": code, "msg": message, "data": None}, status=http_status)


def _error_from_exception(e):
    if isinstance(e, MonitorError):
        return _error(e.message, code=e.code, http_status=e.http_status)
    if isinstance(e, UserError):
        return _error(e.message, code=e.code, http_status=e.http_status)
    return _error(f"服务器错误: {str(e)}", code=500, http_status=500)


def _parse_data(request):
    if request.content_type and "application/json" in request.content_type:
        try:
            body = request.body.decode("utf-8") if request.body else "{}"
            return json.loads(body)
        except json.JSONDecodeError:
            raise MonitorError("请求体不是合法 JSON")
    return request.POST.dict()


def _parse_bool(value, default=None):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    value = str(value).strip().lower()
    if value in ("1", "true", "yes", "on"):
        return True
    if value in ("0", "false", "no", "off"):
        return False
    raise MonitorError("is_active 参数不合法")


def _get_request_user(request, data=None):
    if hasattr(request, "user") and request.user.is_authenticated:
        return request.user

    data = data or {}
    token = (
        data.get("token")
        or request.GET.get("token")
        or request.POST.get("token")
        or request.META.get("HTTP_AUTHORIZATION", "").replace("Bearer ", "")
    )
    if not token:
        raise MonitorError("缺少认证信息", code=401, http_status=401)
    return UserService.get_user_by_token(token)


@csrf_exempt
@require_http_methods(["GET"])
def api_monitor_breeders(request):
    """Admin get breeder list with monitor stats."""
    try:
        user = _get_request_user(request)
        data = MonitorService.list_breeders(user)
        return _success(data)
    except Exception as e:
        return _error_from_exception(e)


@csrf_exempt
@require_http_methods(["GET"])
def api_monitor_devices(request):
    """Admin/Breeder list monitor devices."""
    try:
        user = _get_request_user(request)
        breeder_id = request.GET.get("breeder_id")
        breeder_id = int(breeder_id) if breeder_id else None
        data = MonitorService.list_devices(user, breeder_id=breeder_id)
        return _success(data)
    except ValueError:
        return _error("breeder_id 参数必须是整数")
    except Exception as e:
        return _error_from_exception(e)


@csrf_exempt
@require_http_methods(["POST"])
def api_monitor_create(request):
    """Admin/Breeder create monitor device."""
    try:
        payload = _parse_data(request)
        user = _get_request_user(request, data=payload)
        payload["is_active"] = _parse_bool(payload.get("is_active"), default=True)
        if payload.get("owner_id") is not None:
            payload["owner_id"] = int(payload["owner_id"])
        data = MonitorService.create_device(user, payload)
        return _success(data, msg="创建成功")
    except ValueError:
        return _error("owner_id 参数必须是整数")
    except Exception as e:
        return _error_from_exception(e)


@csrf_exempt
@require_http_methods(["POST"])
def api_monitor_update(request, device_id):
    """Admin/Breeder update monitor device."""
    try:
        payload = _parse_data(request)
        user = _get_request_user(request, data=payload)
        if payload.get("is_active") is not None:
            payload["is_active"] = _parse_bool(payload.get("is_active"))
        if payload.get("owner_id") is not None:
            payload["owner_id"] = int(payload["owner_id"])
        data = MonitorService.update_device(user, device_id=device_id, data=payload)
        return _success(data, msg="更新成功")
    except ValueError:
        return _error("owner_id 参数必须是整数")
    except Exception as e:
        return _error_from_exception(e)


@csrf_exempt
@require_http_methods(["POST"])
def api_monitor_delete(request, device_id):
    """Admin/Breeder delete monitor device."""
    try:
        payload = _parse_data(request)
        user = _get_request_user(request, data=payload)
        data = MonitorService.delete_device(user, device_id=device_id)
        return _success(data, msg="删除成功")
    except Exception as e:
        return _error_from_exception(e)
