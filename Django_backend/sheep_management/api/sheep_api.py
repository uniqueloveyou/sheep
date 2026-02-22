"""
羊只相关 API 接口
薄接口层：解析 HTTP 参数 → 调用 Service → 构建 JsonResponse
"""
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..services.sheep_service import SheepService, SheepError


def _error_response(e):
    """统一构建错误响应"""
    if isinstance(e, SheepError):
        return JsonResponse(
            {'code': e.code, 'msg': e.message, 'data': None},
            status=e.http_status
        )
    return JsonResponse(
        {'code': 500, 'msg': f'服务器错误: {str(e)}', 'data': None},
        status=500
    )


@csrf_exempt
@require_http_methods(["GET"])
def api_search_sheep(request):
    """
    搜索羊只接口
    GET /api/sheep/search
    """
    try:
        result = SheepService.search_sheep(
            gender=request.GET.get('gender', '').strip() or None,
            weight=request.GET.get('weight', '').strip() or None,
            height=request.GET.get('height', '').strip() or None,
            length=request.GET.get('length', '').strip() or None,
        )
        return JsonResponse(result, safe=False, status=200)
    except SheepError as e:
        return _error_response(e)
    except Exception as e:
        return _error_response(e)


@csrf_exempt
@require_http_methods(["GET"])
def api_get_sheep_by_id(request, sheep_id=None):
    """
    根据ID获取羊只详情
    GET /api/sheep/<sheep_id>
    """
    try:
        if not sheep_id:
            sheep_id = request.GET.get('id') or request.GET.get('pk')
        result = SheepService.get_sheep_by_id(sheep_id)
        return JsonResponse(result, status=200)
    except SheepError as e:
        return _error_response(e)
    except Exception as e:
        return _error_response(e)


@csrf_exempt
@require_http_methods(["GET"])
def api_get_vaccine_records(request, sheep_id):
    """
    获取羊只疫苗接种记录
    GET /api/vaccine/records/<sheep_id>
    """
    try:
        result = SheepService.get_vaccine_records(sheep_id)
        return JsonResponse(result, safe=False, status=200)
    except SheepError as e:
        return _error_response(e)
    except Exception as e:
        return _error_response(e)


@csrf_exempt
@require_http_methods(["GET"])
def api_get_sheep_with_growth(request, sheep_id):
    """
    获取羊只完整数据（含生长/喂养/疫苗记录）
    GET /api/growth/sheep/<sheep_id>
    """
    try:
        result = SheepService.get_sheep_with_growth(sheep_id)
        return JsonResponse(result, status=200)
    except SheepError as e:
        return _error_response(e)
    except Exception as e:
        return _error_response(e)


@csrf_exempt
@require_http_methods(["GET"])
def api_get_sheep_by_ear_tag(request):
    """
    根据耳标编号查询羊只信息（供扫码溯源使用）
    GET /api/sheep/trace?ear_tag=TY-2026-001
    """
    try:
        ear_tag = request.GET.get('ear_tag', '').strip()
        result = SheepService.get_sheep_by_ear_tag(
            ear_tag=ear_tag,
            build_absolute_uri=request.build_absolute_uri,
        )
        return JsonResponse(result, status=200)
    except SheepError as e:
        return _error_response(e)
    except Exception as e:
        return _error_response(e)
