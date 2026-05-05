"""Breeder wallet & admin withdrawal management views."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..permissions import admin_required
from ..models import Order
from ..services.wallet_service import WalletError, WalletService


@login_required
def breeder_wallet(request):
    """养殖户钱包页面"""
    user = request.user
    wallet = WalletService.get_breeder_wallet(user)
    withdrawals = WalletService.get_withdrawal_history(user.id)

    # 已结算订单统计
    settled_orders = Order.objects.filter(
        settlement_status="settled",
        items__sheep__owner=user,
    ).distinct().count()

    context = {
        "user": user,
        "wallet": wallet,
        "withdrawals": withdrawals,
        "settled_orders": settled_orders,
    }
    return render(request, "sheep_management/breeder/wallet.html", context)


@login_required
def breeder_withdraw(request):
    """养殖户提现页面"""
    user = request.user

    if request.method == "POST":
        amount = request.POST.get("amount")
        bank_name = request.POST.get("bank_name", "").strip()
        bank_card_no = request.POST.get("bank_card_no", "").strip()
        account_holder = request.POST.get("account_holder", "").strip()

        try:
            result = WalletService.create_withdrawal(user.id, amount, bank_name, bank_card_no, account_holder)
            messages.success(request, f"提现申请已提交，金额：¥{result['amount']}")
            return redirect("breeder_wallet")
        except WalletError as e:
            messages.error(request, e.message)
        except Exception as e:
            messages.error(request, f"提现失败：{str(e)}")

    wallet = WalletService.get_breeder_wallet(user)
    return render(request, "sheep_management/breeder/withdraw.html", {
        "user": user,
        "wallet": wallet,
    })


@login_required
@admin_required
def admin_withdrawal_list(request):
    """管理员提现审核列表"""
    status_filter = request.GET.get("status", "pending")
    withdrawals = WalletService.get_all_withdrawals(status_filter if status_filter else None)
    return render(request, "sheep_management/admin/withdrawal_list.html", {
        "withdrawals": withdrawals,
        "current_status": status_filter,
    })


@login_required
@admin_required
def admin_process_withdrawal(request, withdrawal_id):
    """管理员处理提现"""
    if request.method != "POST":
        messages.error(request, "仅支持POST请求")
        return redirect("admin_withdrawal_list")

    action = request.POST.get("action")
    remark = request.POST.get("remark", "").strip()

    try:
        result = WalletService.process_withdrawal(withdrawal_id, request.user.id, action, remark)
        msg = f"提现申请已{'通过' if action == 'approved' else '拒绝'}"
        messages.success(request, msg)
    except WalletError as e:
        messages.error(request, e.message)
    except Exception as e:
        messages.error(request, f"操作失败：{str(e)}")

    return redirect("admin_withdrawal_list")
