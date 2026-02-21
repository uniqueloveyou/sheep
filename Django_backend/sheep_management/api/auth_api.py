"""
认证相关 API 接口（薄 API 层）
只负责：解析 request → 调 AuthService → 捕获 AuthError → 返回 JsonResponse
"""
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..services.auth_service import AuthService, AuthError


def _error_response(e):
    """统一构建错误响应"""
    if isinstance(e, AuthError):
        return JsonResponse(
            {'code': e.code, 'msg': e.message, 'data': None},
            status=e.http_status
        )
    return JsonResponse(
        {'code': 500, 'msg': f'服务器错误: {str(e)}', 'data': None},
        status=500
    )


@csrf_exempt
@require_http_methods(["POST"])
def api_login_by_phone(request):
    """微信手机号一键登录 POST /api/auth/login_by_phone"""
    try:
        data = json.loads(request.body)
        result = AuthService.login_by_phone(
            code=data.get('code'),
            phone_code=data.get('phoneCode'),
        )
        return JsonResponse({'code': 0, 'msg': '登录成功', 'data': result})
    except (AuthError, json.JSONDecodeError) as e:
        return _error_response(e)
    except Exception as e:
        return _error_response(e)


@csrf_exempt
@require_http_methods(["POST"])
def api_login_wx(request):
    """微信静默登录（仅 code） POST /api/auth/login"""
    try:
        data = json.loads(request.body)
        result = AuthService.login_by_wx_code(code=data.get('code'))
        return JsonResponse({'code': 0, 'msg': '登录成功', 'data': result})
    except (AuthError, json.JSONDecodeError) as e:
        return _error_response(e)
    except Exception as e:
        return _error_response(e)


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """账号密码登录 POST /api/auth/login_password"""
    try:
        data = json.loads(request.body)
        result = AuthService.login_by_password(
            username=data.get('username', '').strip(),
            password=data.get('password', '').strip(),
        )
        return JsonResponse({'code': 0, 'msg': '登录成功', 'data': result})
    except (AuthError, json.JSONDecodeError) as e:
        return _error_response(e)
    except Exception as e:
        return _error_response(e)


@csrf_exempt
@require_http_methods(["POST"])
def api_register(request):
    """用户注册 POST /api/auth/register"""
    try:
        data = json.loads(request.body)
        result = AuthService.register(
            username=data.get('username', '').strip(),
            password=data.get('password', '').strip(),
            mobile=data.get('mobile', '').strip() or None,
            nickname=data.get('nickname', '').strip() or None,
        )
        return JsonResponse({'code': 0, 'msg': '注册成功', 'data': result})
    except (AuthError, json.JSONDecodeError) as e:
        return _error_response(e)
    except Exception as e:
        return _error_response(e)


@csrf_exempt
@require_http_methods(["POST", "GET"])
def api_check_token(request):
    """验证 Token POST/GET /api/auth/check_token"""
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            token = data.get('token', '').strip()
        else:
            token = request.GET.get('token', '').strip()

        result = AuthService.check_token(token)
        return JsonResponse({'code': 0, 'msg': 'token有效', 'data': result})
    except (AuthError, json.JSONDecodeError) as e:
        return _error_response(e)
    except Exception as e:
        return _error_response(e)
