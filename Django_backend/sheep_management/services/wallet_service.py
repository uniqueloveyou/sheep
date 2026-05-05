from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from ..models import Order, OrderItem, Sheep, User, Withdrawal
from .user_service import UserError, UserService


class WalletError(Exception):
    def __init__(self, message, code=400, http_status=400):
        self.message = message
        self.code = code
        self.http_status = http_status
        super().__init__(message)


class WalletService:
    PLATFORM_COMMISSION_RATE = Decimal("0.10")  # 平台抽成 10%

    @staticmethod
    def get_breeder_wallet(breeder):
        """获取养殖户钱包信息"""
        return {
            "balance": float(breeder.breeder_balance or 0),
            "total_earned": float(breeder.total_earned or 0),
        }

    @staticmethod
    @transaction.atomic
    def settle_order(order_id):
        """结算订单收入到养殖户钱包（下单付款时触发）"""
        try:
            order = Order.objects.select_for_update().get(pk=order_id)
        except Order.DoesNotExist as exc:
            raise WalletError("订单不存在", code=404, http_status=404) from exc

        if order.settlement_status == "settled":
            raise WalletError("该订单已结算，请勿重复操作")

        total_revenue = (order.total_amount or Decimal("0")) + (order.care_fee_amount or Decimal("0"))
        if total_revenue <= 0:
            raise WalletError("无可结算的金额")

        platform_fee = (total_revenue * WalletService.PLATFORM_COMMISSION_RATE).quantize(Decimal("0.01"))
        breeder_earnings = (total_revenue - platform_fee).quantize(Decimal("0.01"))

        # 按羊只所属养殖户分配
        order_items = OrderItem.objects.filter(order=order).select_related("sheep__owner")
        breeder_amounts = WalletService._distribute_earnings(order_items, breeder_earnings, total_revenue)

        # 入账到各养殖户
        WalletService._credit_breeders(breeder_amounts)

        # 更新订单结算状态
        now = timezone.now()
        order.breeder_earnings = breeder_earnings
        order.platform_fee = platform_fee
        order.settlement_status = "settled"
        order.settled_at = now
        order.save(update_fields=["breeder_earnings", "platform_fee", "settlement_status", "settled_at"])

        return {
            "order_id": order.id,
            "total_revenue": float(total_revenue),
            "platform_fee": float(platform_fee),
            "breeder_earnings": float(breeder_earnings),
            "settled_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        }

    @staticmethod
    @transaction.atomic
    def settle_care_fee(order_id):
        """结算照料费到养殖户钱包（照料费支付时触发，属额外追加）"""
        try:
            order = Order.objects.select_for_update().get(pk=order_id)
        except Order.DoesNotExist as exc:
            raise WalletError("订单不存在", code=404, http_status=404) from exc

        care_fee = order.care_fee_amount or Decimal("0")
        if care_fee <= 0:
            raise WalletError("无可结算的照料费")

        # 计算照料费中养殖户应得部分
        platform_fee = (care_fee * WalletService.PLATFORM_COMMISSION_RATE).quantize(Decimal("0.01"))
        breeder_earnings = (care_fee - platform_fee).quantize(Decimal("0.01"))

        # 按羊只分配
        order_items = OrderItem.objects.filter(order=order).select_related("sheep__owner")
        total_order = (order.total_amount or Decimal("0")) + care_fee
        breeder_amounts = WalletService._distribute_earnings(order_items, breeder_earnings, total_order)

        # 入账（追加到已有余额中）
        WalletService._credit_breeders(breeder_amounts)

        # 更新订单累计结算金额
        order.breeder_earnings = (order.breeder_earnings or Decimal("0")) + breeder_earnings
        order.platform_fee = (order.platform_fee or Decimal("0")) + platform_fee
        order.save(update_fields=["breeder_earnings", "platform_fee"])

        return {
            "order_id": order.id,
            "care_fee": float(care_fee),
            "platform_fee": float(platform_fee),
            "breeder_earnings": float(breeder_earnings),
        }

    @staticmethod
    def _distribute_earnings(order_items, total_earnings, total_revenue):
        """按羊只价格占比分配收入到各养殖户"""
        item_list = list(order_items)
        total = total_revenue if total_revenue > 0 else Decimal("1")
        amounts = {}
        for item in item_list:
            owner = item.sheep.owner
            if not owner or owner.role != 1:
                continue
            ratio = item.price / total
            item_share = (total_earnings * ratio).quantize(Decimal("0.01"))
            if owner.id not in amounts:
                amounts[owner.id] = {"breeder": owner, "amount": Decimal("0")}
            amounts[owner.id]["amount"] += item_share
        return amounts

    @staticmethod
    def _credit_breeders(breeder_amounts):
        """将金额入账到各养殖户钱包"""
        for info in breeder_amounts.values():
            breeder = User.objects.select_for_update().get(pk=info["breeder"].id)
            breeder.breeder_balance = (breeder.breeder_balance or Decimal("0")) + info["amount"]
            breeder.total_earned = (breeder.total_earned or Decimal("0")) + info["amount"]
            breeder.save(update_fields=["breeder_balance", "total_earned"])

    @staticmethod
    @transaction.atomic
    def create_withdrawal(breeder_id, amount, bank_name, bank_card_no, account_holder):
        """养殖户发起提现申请"""
        try:
            breeder = User.objects.select_for_update().get(pk=breeder_id, role=1)
        except User.DoesNotExist as exc:
            raise WalletError("养殖户不存在", code=404, http_status=404) from exc

        amount = Decimal(str(amount))
        if amount <= 0:
            raise WalletError("提现金额必须大于0")
        if amount > (breeder.breeder_balance or Decimal("0")):
            raise WalletError("可提现余额不足")

        if not bank_name or not bank_card_no or not account_holder:
            raise WalletError("请完整填写收款信息")

        # 冻结余额
        breeder.breeder_balance -= amount
        breeder.save(update_fields=["breeder_balance"])

        withdrawal = Withdrawal.objects.create(
            breeder=breeder,
            amount=amount,
            status="pending",
            bank_name=bank_name.strip(),
            bank_card_no=bank_card_no.strip(),
            account_holder=account_holder.strip(),
        )
        return WalletService._build_withdrawal(withdrawal)

    @staticmethod
    def get_withdrawal_history(breeder_id):
        """获取养殖户提现记录"""
        withdrawals = Withdrawal.objects.filter(breeder_id=breeder_id).order_by("-created_at")
        return [WalletService._build_withdrawal(w) for w in withdrawals]

    @staticmethod
    def get_pending_withdrawals():
        """管理员：获取所有待审核提现"""
        withdrawals = Withdrawal.objects.filter(status="pending").select_related("breeder").order_by("-created_at")
        return [WalletService._build_withdrawal(w) for w in withdrawals]

    @staticmethod
    def get_all_withdrawals(status=None):
        """管理员：获取所有提现记录，可按状态筛选"""
        qs = Withdrawal.objects.select_related("breeder", "processed_by").order_by("-created_at")
        if status:
            qs = qs.filter(status=status)
        return [WalletService._build_withdrawal(w) for w in qs]

    @staticmethod
    @transaction.atomic
    def process_withdrawal(withdrawal_id, admin_id, action, remark=None):
        """管理员审核提现"""
        try:
            withdrawal = Withdrawal.objects.select_for_update().get(pk=withdrawal_id, status="pending")
        except Withdrawal.DoesNotExist as exc:
            raise WalletError("提现申请不存在或已处理", code=404, http_status=404) from exc

        if action == "approved":
            withdrawal.status = "approved"
        elif action == "rejected":
            withdrawal.status = "rejected"
            # 拒绝时退回余额
            breeder = User.objects.select_for_update().get(pk=withdrawal.breeder_id)
            breeder.breeder_balance += withdrawal.amount
            breeder.save(update_fields=["breeder_balance"])
        else:
            raise WalletError("操作类型不正确，请使用 approved 或 rejected")

        withdrawal.remark = remark
        withdrawal.processed_by_id = admin_id
        withdrawal.processed_at = timezone.now()
        withdrawal.save(update_fields=["status", "remark", "processed_by", "processed_at"])

        return WalletService._build_withdrawal(withdrawal)

    @staticmethod
    def _build_withdrawal(w):
        data = {
            "id": w.id,
            "amount": float(w.amount),
            "status": w.status,
            "status_display": w.get_status_display(),
            "bank_name": w.bank_name,
            "bank_card_no": w.bank_card_no,
            "account_holder": w.account_holder,
            "remark": w.remark or "",
            "created_at": w.created_at.strftime("%Y-%m-%d %H:%M:%S") if w.created_at else "",
            "processed_at": w.processed_at.strftime("%Y-%m-%d %H:%M:%S") if w.processed_at else "",
        }
        if hasattr(w, 'breeder') and w.breeder:
            data["breeder"] = {
                "id": w.breeder.id,
                "nickname": w.breeder.nickname or w.breeder.username,
                "mobile": w.breeder.mobile or "",
            }
        if w.processed_by:
            data["processed_by"] = w.processed_by.nickname or w.processed_by.username
        return data
