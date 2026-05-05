"""Wallet / withdrawal API endpoints for the Mini Program."""
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..services.user_service import UserService
from ..services.wallet_service import WalletError, WalletService


@csrf_exempt
@require_http_methods(["GET"])
def api_breeder_wallet(request):
    """GET /api/breeder/wallet - 获取养殖户钱包信息"""
    try:
        token = _get_token(request)
        user = UserService.get_user_by_token(token)
        if user.role != 1:
            return JsonResponse({"code": 403, "msg": "仅养殖户可查看钱包"}, status=403)
        data = WalletService.get_breeder_wallet(user)
        return JsonResponse({"code": 0, "data": data})
    except WalletError as e:
        return JsonResponse({"code": e.code, "msg": e.message}, status=e.http_status)
    except Exception as e:
        return JsonResponse({"code": 500, "msg": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_breeder_withdraw(request):
    """POST /api/breeder/withdraw - 养殖户发起提现"""
    try:
        token = _get_token(request)
        user = UserService.get_user_by_token(token)
        if user.role != 1:
            return JsonResponse({"code": 403, "msg": "仅养殖户可提现"}, status=403)

        data = json.loads(request.body) if request.body else {}
        amount = data.get("amount")
        bank_name = data.get("bank_name", "").strip()
        bank_card_no = data.get("bank_card_no", "").strip()
        account_holder = data.get("account_holder", "").strip()

        result = WalletService.create_withdrawal(user.id, amount, bank_name, bank_card_no, account_holder)
        return JsonResponse({"code": 0, "data": result})
    except WalletError as e:
        return JsonResponse({"code": e.code, "msg": e.message}, status=e.http_status)
    except Exception as e:
        return JsonResponse({"code": 500, "msg": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_breeder_withdraw_history(request):
    """GET /api/breeder/withdraw/history - 养殖户提现记录"""
    try:
        token = _get_token(request)
        user = UserService.get_user_by_token(token)
        if user.role != 1:
            return JsonResponse({"code": 403, "msg": "仅养殖户可查看"}, status=403)
        records = WalletService.get_withdrawal_history(user.id)
        return JsonResponse({"code": 0, "data": records})
    except WalletError as e:
        return JsonResponse({"code": e.code, "msg": e.message}, status=e.http_status)
    except Exception as e:
        return JsonResponse({"code": 500, "msg": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_admin_withdrawals(request):
    """GET /api/admin/withdrawals - 管理员获取提现列表"""
    try:
        token = _get_token(request)
        user = UserService.get_user_by_token(token)
        if user.role != 2:
            return JsonResponse({"code": 403, "msg": "仅管理员可查看"}, status=403)
        status = request.GET.get("status")
        records = WalletService.get_all_withdrawals(status)
        return JsonResponse({"code": 0, "data": records})
    except WalletError as e:
        return JsonResponse({"code": e.code, "msg": e.message}, status=e.http_status)
    except Exception as e:
        return JsonResponse({"code": 500, "msg": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_admin_process_withdrawal(request, withdrawal_id):
    """POST /api/admin/withdrawals/<id>/process - 管理员审核提现"""
    try:
        token = _get_token(request)
        admin = UserService.get_user_by_token(token)
        if admin.role != 2:
            return JsonResponse({"code": 403, "msg": "仅管理员可审核"}, status=403)

        data = json.loads(request.body) if request.body else {}
        action = data.get("action")  # "approved" or "rejected"
        remark = data.get("remark", "")

        result = WalletService.process_withdrawal(withdrawal_id, admin.id, action, remark)
        return JsonResponse({"code": 0, "data": result})
    except WalletError as e:
        return JsonResponse({"code": e.code, "msg": e.message}, status=e.http_status)
    except Exception as e:
        return JsonResponse({"code": 500, "msg": str(e)}, status=500)


def _get_token(request):
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    # also check query param
    token = request.GET.get("token")
    if token:
        return token
    raise WalletError("未提供认证令牌", code=401, http_status=401)
