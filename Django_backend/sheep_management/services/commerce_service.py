import re
import uuid
from datetime import timedelta
from decimal import Decimal, ROUND_CEILING

from django.db import transaction
from django.db.models import Count, Max
from django.utils import timezone

from ..models import (
    CartItem,
    FeedingRecord,
    GrowthRecord,
    Order,
    OrderItem,
    Sheep,
    UserCoupon,
    VaccinationHistory,
)
from .user_service import UserError, UserService


class CommerceError(Exception):
    def __init__(self, message, code=400, http_status=400):
        self.message = message
        self.code = code
        self.http_status = http_status
        super().__init__(message)


class CommerceService:
    CART_RESERVATION_MINUTES = 30
    DEFAULT_DAILY_CARE_FEE = Decimal("10.00")
    ACTIVE_ADOPTION_STATUSES = ["paid", "adopting", "ready_to_ship", "settlement_pending", "awaiting_delivery"]
    ADOPTED_ORDER_STATUSES = ACTIVE_ADOPTION_STATUSES + ["shipping", "completed"]
    ORDER_STATUS_DISPLAY = {
        "pending": "待支付",
        "paid": "认养中",
        "adopting": "认养中",
        "ready_to_ship": "认养中",
        "settlement_pending": "待结算",
        "awaiting_delivery": "待交付",
        "shipping": "交付中",
        "completed": "已完成",
        "cancelled": "已取消",
    }
    DELIVERY_METHOD_DISPLAY = {
        "logistics": "物流配送",
        "offline": "线下交付",
    }
    ORDER_TRANSITIONS = {
        "pending": ["adopting", "cancelled"],
        "paid": ["settlement_pending", "ready_to_ship", "cancelled"],
        "adopting": ["settlement_pending", "ready_to_ship", "cancelled"],
        "ready_to_ship": ["settlement_pending", "awaiting_delivery", "cancelled"],
        "settlement_pending": ["awaiting_delivery", "cancelled"],
        "awaiting_delivery": ["shipping", "cancelled"],
        "shipping": ["completed"],
        "completed": [],
        "cancelled": [],
    }

    @staticmethod
    def add_to_cart(token, sheep_id, quantity=1, price=None):
        user = CommerceService._resolve_user(token)
        if not sheep_id:
            raise CommerceError("缺少羊只编号")

        try:
            sheep = Sheep.objects.get(pk=sheep_id)
        except Sheep.DoesNotExist as exc:
            raise CommerceError("未找到羊只", code=404, http_status=404) from exc

        if CommerceService._has_active_adoption(sheep.id):
            raise CommerceError("该羊只已被领养，不能重复加入购物车。")

        reserved_item = CommerceService._get_active_cart_reservation(sheep.id, exclude_user_id=user.id)
        if reserved_item:
            raise CommerceError("该羊只已被其他用户暂时锁定，请稍后再试。")

        existing = CartItem.objects.filter(user=user, sheep=sheep).first()
        if existing:
            existing.quantity = 1
            existing.save(update_fields=["quantity", "updated_at"])
            return CommerceService._build_cart_item(existing)

        resolved_price = Decimal(str(price)) if price not in (None, 0, "0", "0.00") else (sheep.price or Decimal("0"))
        cart_item = CartItem.objects.create(
            user=user,
            sheep=sheep,
            quantity=1,
            price=resolved_price,
        )
        return CommerceService._build_cart_item(cart_item)

    @staticmethod
    def get_cart(token):
        user = CommerceService._resolve_user(token)
        items = CartItem.objects.filter(user=user).select_related("sheep").order_by("-created_at")
        return [CommerceService._build_cart_item(item) for item in items]

    @staticmethod
    def remove_from_cart(token, cart_item_id):
        user = CommerceService._resolve_user(token)
        try:
            item = CartItem.objects.get(pk=cart_item_id, user=user)
        except CartItem.DoesNotExist as exc:
            raise CommerceError("未找到购物车商品", code=404, http_status=404) from exc
        item.delete()

    @staticmethod
    def update_cart_item(token, cart_item_id, quantity):
        user = CommerceService._resolve_user(token)
        if int(quantity or 0) != 1:
            raise CommerceError("单只羊认养数量只能为 1")

        try:
            item = CartItem.objects.get(pk=cart_item_id, user=user)
        except CartItem.DoesNotExist as exc:
            raise CommerceError("未找到购物车商品", code=404, http_status=404) from exc

        item.quantity = 1
        item.save(update_fields=["quantity", "updated_at"])
        return CommerceService._build_cart_item(item)

    @staticmethod
    def get_sheep_adopt_status(token, sheep_id):
        return CommerceService.get_sheep_adopt_status_v2(token, sheep_id)

    @staticmethod
    def get_sheep_adopt_status_v2(token, sheep_id):
        if not sheep_id:
            raise CommerceError("缺少羊只编号")

        try:
            sheep = Sheep.objects.get(pk=sheep_id)
        except Sheep.DoesNotExist as exc:
            raise CommerceError("未找到羊只", code=404, http_status=404) from exc

        current_user = None
        if token:
            try:
                current_user = UserService.get_user_by_token(token)
            except Exception:
                current_user = None

        adopted_order_item = (
            OrderItem.objects.filter(
                sheep=sheep,
                order__status__in=CommerceService.ADOPTED_ORDER_STATUSES,
            )
            .select_related("order__user")
            .first()
        )
        if adopted_order_item:
            if current_user and adopted_order_item.order.user_id == current_user.id:
                return {"status": "adopted_by_me", "status_text": "我已领养"}
            return {"status": "adopted_by_others", "status_text": "已被领养"}

        if current_user:
            in_cart = CartItem.objects.filter(user=current_user, sheep=sheep).exists()
            if in_cart:
                return {"status": "in_my_cart", "status_text": "已在购物车中"}

        reserved_item = CommerceService._get_active_cart_reservation(
            sheep.id,
            exclude_user_id=current_user.id if current_user else None,
        )
        if reserved_item:
            return {"status": "reserved_by_others", "status_text": "已被暂时锁定"}

        return {"status": "available", "status_text": "可领养"}

    @staticmethod
    @transaction.atomic
    def checkout(
        token,
        payment_method="balance",
        receiver_name=None,
        receiver_phone=None,
        shipping_address=None,
        user_coupon_id=None,
        selected_cart_item_ids=None,
    ):
        user = CommerceService._resolve_user(token)
        receiver_name, receiver_phone, shipping_address = CommerceService._validate_checkout_fields(
            receiver_name,
            receiver_phone,
            shipping_address,
        )

        cart_items = CartItem.objects.select_for_update().filter(user=user).select_related("sheep")
        selected_cart_item_ids = CommerceService._normalize_cart_item_ids(selected_cart_item_ids)
        if selected_cart_item_ids:
            cart_items = cart_items.filter(id__in=selected_cart_item_ids)
        cart_items = list(cart_items)
        if not cart_items:
            raise CommerceError("购物车为空")
        if selected_cart_item_ids and len(cart_items) != len(selected_cart_item_ids):
            raise CommerceError("部分已选商品已失效，请重新勾选后再试。")

        CommerceService._assert_cart_items_available(user, cart_items)

        total_amount = sum((item.price * item.quantity for item in cart_items), Decimal("0"))
        discount_amount = Decimal("0")
        used_coupon = None

        if user_coupon_id:
            try:
                used_coupon = UserCoupon.objects.select_related("coupon").get(pk=user_coupon_id, user=user)
            except UserCoupon.DoesNotExist as exc:
                raise CommerceError("未找到该优惠券，或该优惠券不属于当前用户。") from exc

            if used_coupon.status != "unused":
                raise CommerceError("该优惠券已使用或已失效。")
            if used_coupon.coupon.valid_until < timezone.now():
                used_coupon.status = "expired"
                used_coupon.save(update_fields=["status"])
                raise CommerceError("该优惠券已过期。")

            coupon = used_coupon.coupon
            if coupon.owner_id:
                applicable_items = [item for item in cart_items if item.sheep.owner_id == coupon.owner_id]
                if not applicable_items:
                    owner_name = coupon.owner.nickname or coupon.owner.username
                    raise CommerceError(f"该优惠券仅限养殖户“{owner_name}”的羊只使用。")
            else:
                applicable_items = cart_items

            applicable_amount = sum((item.price * item.quantity for item in applicable_items), Decimal("0"))
            if applicable_amount < coupon.min_purchase_amount:
                raise CommerceError(f"未达到优惠券使用门槛：满 {coupon.min_purchase_amount} 元可用。")

            if coupon.coupon_type in {"discount", "cash"}:
                discount_amount = coupon.discount_amount or Decimal("0")
            elif coupon.coupon_type == "percentage" and coupon.discount_rate:
                discount_amount = applicable_amount * (Decimal("1") - Decimal(str(coupon.discount_rate)))
                if coupon.max_discount_amount and discount_amount > coupon.max_discount_amount:
                    discount_amount = coupon.max_discount_amount

            discount_amount = min(discount_amount, applicable_amount, total_amount)

        final_amount = max(total_amount - discount_amount, Decimal("0"))
        order_daily_care_fee = CommerceService._resolve_order_daily_care_fee(cart_items)

        if payment_method == "balance":
            if user.balance < final_amount:
                raise CommerceError("余额不足。")
            user.balance -= final_amount
            user.save(update_fields=["balance"])
            order_status = "adopting"
            pay_time = timezone.now()
        elif payment_method == "wechat":
            order_status = "pending"
            pay_time = None
        else:
            raise CommerceError("不支持的支付方式。")

        order = Order.objects.create(
            user=user,
            order_no=f"ORD-{uuid.uuid4().hex[:12].upper()}",
            total_amount=final_amount,
            status=order_status,
            pay_time=pay_time,
            adoption_start_time=pay_time,
            daily_care_fee=order_daily_care_fee,
            receiver_name=receiver_name,
            receiver_phone=receiver_phone,
            shipping_address=shipping_address,
        )

        if used_coupon:
            used_coupon.status = "used"
            used_coupon.used_at = timezone.now()
            used_coupon.order_id = order.id
            used_coupon.save(update_fields=["status", "used_at", "order_id"])

        for item in cart_items:
            OrderItem.objects.create(order=order, sheep=item.sheep, price=item.price)

        CartItem.objects.filter(id__in=[item.id for item in cart_items]).delete()
        return CommerceService._build_order(order)

    @staticmethod
    @transaction.atomic
    def request_end_adoption(token, order_id, delivery_info=None):
        user = CommerceService._resolve_user(token)
        try:
            order = Order.objects.select_for_update().get(pk=order_id, user=user)
        except Order.DoesNotExist as exc:
            raise CommerceError("未找到认养订单", code=404, http_status=404) from exc

        if order.status not in {"paid", "adopting", "ready_to_ship"}:
            raise CommerceError("当前认养状态不能申请结束。")

        delivery_info = delivery_info or {}
        receiver_name = (delivery_info.get("receiver_name") or order.receiver_name or "").strip()
        receiver_phone = (delivery_info.get("receiver_phone") or order.receiver_phone or "").strip()
        shipping_address = (delivery_info.get("shipping_address") or order.shipping_address or "").strip()
        if not receiver_name:
            raise CommerceError("请填写收货人姓名。")
        if not receiver_phone:
            raise CommerceError("请填写联系电话。")
        if not shipping_address:
            raise CommerceError("请填写收货地址。")

        now = timezone.now()
        order.adoption_start_time = order.adoption_start_time or order.pay_time or order.created_at or now
        order.end_requested_at = now
        care_fee_amount = CommerceService._calculate_care_fee(order, now)[1]
        order.care_fee_amount = care_fee_amount
        order.receiver_name = receiver_name
        order.receiver_phone = receiver_phone
        order.shipping_address = shipping_address
        order.delivery_method = "logistics"
        order.offline_delivery_location = ""
        order.offline_delivery_note = ""
        order.status = "settlement_pending"
        order.save(update_fields=[
            "adoption_start_time",
            "end_requested_at",
            "care_fee_amount",
            "receiver_name",
            "receiver_phone",
            "shipping_address",
            "delivery_method",
            "offline_delivery_location",
            "offline_delivery_note",
            "status",
        ])
        return CommerceService._build_order(order)

    @staticmethod
    @transaction.atomic
    def pay_care_fee(token, order_id, payment_method="balance"):
        user = CommerceService._resolve_user(token)
        try:
            order = Order.objects.select_for_update().get(pk=order_id, user=user)
        except Order.DoesNotExist as exc:
            raise CommerceError("未找到认养订单", code=404, http_status=404) from exc

        if order.status != "settlement_pending":
            raise CommerceError("当前订单不处于待结算状态。")
        if payment_method != "balance":
            raise CommerceError("当前仅支持余额支付周期服务费。")

        care_fee_amount = order.care_fee_amount or Decimal("0")
        if user.balance < care_fee_amount:
            raise CommerceError("余额不足，无法支付周期服务费。")

        user.balance -= care_fee_amount
        user.save(update_fields=["balance"])
        order.status = "awaiting_delivery"
        order.care_fee_paid_at = timezone.now()
        order.save(update_fields=["status", "care_fee_paid_at"])
        return CommerceService._build_order(order)

    @staticmethod
    def get_my_sheep(token):
        user = CommerceService._resolve_user(token)
        order_items = (
            OrderItem.objects.filter(
                order__user=user,
                order__status__in=CommerceService.ADOPTED_ORDER_STATUSES,
            )
            .select_related("sheep__owner", "order")
            .order_by("-order__created_at")
        )

        result = []
        for order_item in order_items:
            sheep = order_item.sheep
            adoption_days, estimated_care_fee = CommerceService._calculate_care_fee(order_item.order)
            result.append(
                {
                    "id": order_item.id,
                    "order_id": order_item.order.id,
                    "order_no": order_item.order.order_no,
                    "order_status": CommerceService.ORDER_STATUS_DISPLAY.get(
                        order_item.order.status, order_item.order.status
                    ),
                    "order_status_key": order_item.order.status,
                    "price": float(order_item.price),
                    "total_amount": float(order_item.order.total_amount or 0),
                    "final_amount": float(
                        (order_item.order.total_amount or Decimal("0"))
                        + (order_item.order.care_fee_amount or Decimal("0"))
                    ),
                    "daily_care_fee": float(order_item.order.daily_care_fee or 0),
                    "care_fee_amount": float(order_item.order.care_fee_amount or 0),
                    "estimated_care_fee": float(estimated_care_fee),
                    "adoption_days": adoption_days,
                    "delivery_method": order_item.order.delivery_method or "logistics",
                    "delivery_method_display": CommerceService.DELIVERY_METHOD_DISPLAY.get(
                        order_item.order.delivery_method or "logistics",
                        "物流配送",
                    ),
                    "end_requested_at": order_item.order.end_requested_at.strftime("%Y-%m-%d %H:%M")
                    if order_item.order.end_requested_at
                    else "",
                    "care_fee_paid_at": order_item.order.care_fee_paid_at.strftime("%Y-%m-%d %H:%M")
                    if order_item.order.care_fee_paid_at
                    else "",
                    "adoption_start_time": order_item.order.adoption_start_time.strftime("%Y-%m-%d %H:%M")
                    if order_item.order.adoption_start_time
                    else "",
                    "pay_time": order_item.order.pay_time.strftime("%Y-%m-%d %H:%M")
                    if order_item.order.pay_time
                    else "",
                    "shipping_date": order_item.order.shipping_date.strftime("%Y-%m-%d %H:%M")
                    if order_item.order.shipping_date
                    else "",
                    "delivery_date": order_item.order.delivery_date.strftime("%Y-%m-%d %H:%M")
                    if order_item.order.delivery_date
                    else "",
                    "sheep": {
                        "id": sheep.id,
                        "ear_tag": sheep.ear_tag,
                        "gender": sheep.get_gender_display(),
                        "weight": float(sheep.current_weight),
                        "height": float(sheep.current_height),
                        "length": float(sheep.current_length),
                        "age_weeks": sheep.age_weeks,
                        "age_display": sheep.age_display,
                        "price": float(sheep.price),
                        "image": sheep.image.url if sheep.image else "",
                        "breeder_id": sheep.owner_id,
                        "breeder_name": sheep.owner.nickname or sheep.owner.username if sheep.owner else "",
                        "breeder_mobile": sheep.owner.mobile if sheep.owner else "",
                        "farm_name": sheep.farm_name or "",
                    },
                    "logistics_company": order_item.order.logistics_company or "",
                    "logistics_tracking_number": order_item.order.logistics_tracking_number or "",
                    "offline_delivery_location": order_item.order.offline_delivery_location or "",
                    "offline_delivery_note": order_item.order.offline_delivery_note or "",
                    "receiver_name": order_item.order.receiver_name or "",
                    "receiver_phone": order_item.order.receiver_phone or "",
                    "shipping_address": order_item.order.shipping_address or "",
                    "created_at": order_item.order.created_at.strftime("%Y-%m-%d %H:%M")
                    if order_item.order.created_at
                    else "",
                }
            )
        return result

    @staticmethod
    def get_my_sheep_trace_updates(token):
        user = CommerceService._resolve_user(token)
        sheep_ids = list(
            OrderItem.objects.filter(
                order__user=user,
                order__status__in=CommerceService.ADOPTED_ORDER_STATUSES,
            )
            .values_list("sheep_id", flat=True)
            .distinct()
        )
        if not sheep_ids:
            return {"total": 0, "updates": []}

        growth_rows = GrowthRecord.objects.filter(sheep_id__in=sheep_ids).values("sheep_id").annotate(
            latest_date=Max("record_date"),
            total=Count("id"),
        )
        feeding_rows = FeedingRecord.objects.filter(sheep_id__in=sheep_ids).values("sheep_id").annotate(
            latest_date=Max("feed_date"),
            total=Count("id"),
        )
        vaccination_rows = VaccinationHistory.objects.filter(sheep_id__in=sheep_ids).values("sheep_id").annotate(
            latest_date=Max("vaccination_date"),
            total=Count("id"),
        )

        growth_map = {
            row["sheep_id"]: {"date": row["latest_date"], "count": row["total"], "type": "growth", "label": "Growth"}
            for row in growth_rows
        }
        feeding_map = {
            row["sheep_id"]: {"date": row["latest_date"], "count": row["total"], "type": "feeding", "label": "Feeding"}
            for row in feeding_rows
        }
        vaccination_map = {
            row["sheep_id"]: {
                "date": row["latest_date"],
                "count": row["total"],
                "type": "vaccination",
                "label": "Vaccination",
            }
            for row in vaccination_rows
        }

        updates = []
        for sheep_id in sheep_ids:
            candidates = [growth_map.get(sheep_id), feeding_map.get(sheep_id), vaccination_map.get(sheep_id)]
            candidates = [item for item in candidates if item and item.get("date")]
            latest = max(candidates, key=lambda item: item["date"]) if candidates else None
            trace_record_count = (
                growth_map.get(sheep_id, {}).get("count", 0)
                + feeding_map.get(sheep_id, {}).get("count", 0)
                + vaccination_map.get(sheep_id, {}).get("count", 0)
            )
            updates.append(
                {
                    "sheep_id": sheep_id,
                    "latest_update_date": latest["date"].strftime("%Y-%m-%d") if latest else "",
                    "latest_update_type": latest["type"] if latest else "",
                    "latest_update_label": latest["label"] if latest else "",
                    "trace_record_count": trace_record_count,
                    "has_trace_data": trace_record_count > 0,
                }
            )

        return {"total": len(updates), "updates": updates}

    @staticmethod
    def get_order_history(token):
        user = CommerceService._resolve_user(token)
        orders = Order.objects.filter(user=user).order_by("-created_at")

        result = []
        for order in orders:
            items = order.items.select_related("sheep__owner").all()
            adoption_days, estimated_care_fee = CommerceService._calculate_care_fee(order)
            result.append(
                {
                    "id": order.id,
                    "order_no": order.order_no,
                    "total_amount": float(order.total_amount),
                    "final_amount": float((order.total_amount or Decimal("0")) + (order.care_fee_amount or Decimal("0"))),
                    "daily_care_fee": float(order.daily_care_fee or 0),
                    "care_fee_amount": float(order.care_fee_amount or 0),
                    "estimated_care_fee": float(estimated_care_fee),
                    "adoption_days": adoption_days,
                    "adoption_start_time": order.adoption_start_time.strftime("%Y-%m-%d %H:%M")
                    if order.adoption_start_time
                    else "",
                    "end_requested_at": order.end_requested_at.strftime("%Y-%m-%d %H:%M")
                    if order.end_requested_at
                    else "",
                    "care_fee_paid_at": order.care_fee_paid_at.strftime("%Y-%m-%d %H:%M")
                    if order.care_fee_paid_at
                    else "",
                    "status": order.status,
                    "status_display": CommerceService.ORDER_STATUS_DISPLAY.get(order.status, order.status),
                    "pay_time": order.pay_time.strftime("%Y-%m-%d %H:%M") if order.pay_time else "",
                    "shipping_date": order.shipping_date.strftime("%Y-%m-%d %H:%M") if order.shipping_date else "",
                    "delivery_date": order.delivery_date.strftime("%Y-%m-%d %H:%M") if order.delivery_date else "",
                    "delivery_method": order.delivery_method or "logistics",
                    "delivery_method_display": CommerceService.DELIVERY_METHOD_DISPLAY.get(
                        order.delivery_method or "logistics",
                        "物流配送",
                    ),
                    "logistics_company": order.logistics_company or "",
                    "logistics_tracking_number": order.logistics_tracking_number or "",
                    "offline_delivery_location": order.offline_delivery_location or "",
                    "offline_delivery_note": order.offline_delivery_note or "",
                    "receiver_name": order.receiver_name or "",
                    "receiver_phone": order.receiver_phone or "",
                    "shipping_address": order.shipping_address or "",
                    "created_at": order.created_at.strftime("%Y-%m-%d %H:%M") if order.created_at else "",
                    "items": [
                        {
                            "sheep_id": item.sheep.id,
                            "ear_tag": item.sheep.ear_tag,
                            "gender": item.sheep.get_gender_display(),
                            "weight": float(item.sheep.current_weight),
                            "health_status": item.sheep.health_status,
                            "price": float(item.price),
                            "breeder_id": item.sheep.owner_id,
                            "breeder_name": item.sheep.owner.nickname or item.sheep.owner.username
                            if item.sheep.owner
                            else "",
                            "breeder_mobile": item.sheep.owner.mobile if item.sheep.owner else "",
                            "farm_name": item.sheep.farm_name or "",
                        }
                        for item in items
                    ],
                }
            )
        return result

    @staticmethod
    def get_breeder_orders(token):
        breeder = CommerceService._resolve_user(token)
        if breeder.role != 1:
            raise CommerceError("只有养殖户可以查看养殖户订单。", code=403, http_status=403)

        sheep_ids = Sheep.objects.filter(owner=breeder).values_list("id", flat=True)
        order_items = (
            OrderItem.objects.filter(sheep_id__in=sheep_ids)
            .select_related("order__user", "sheep")
            .order_by("-order__created_at")
        )

        result = []
        for order_item in order_items:
            order = order_item.order
            result.append(
                {
                    "id": order.id,
                    "order_no": order.order_no,
                    "total_amount": float(order.total_amount),
                    "final_amount": float((order.total_amount or Decimal("0")) + (order.care_fee_amount or Decimal("0"))),
                    "daily_care_fee": float(order.daily_care_fee or 0),
                    "care_fee_amount": float(order.care_fee_amount or 0),
                    "status": order.status,
                    "status_display": CommerceService.ORDER_STATUS_DISPLAY.get(order.status, order.status),
                    "created_at": order.created_at.strftime("%Y-%m-%d %H:%M") if order.created_at else "",
                    "user": {
                        "id": order.user.id,
                        "nickname": order.user.nickname or order.user.username,
                        "mobile": order.user.mobile or "",
                    },
                    "sheep": {
                        "id": order_item.sheep.id,
                        "ear_tag": order_item.sheep.ear_tag,
                        "gender": order_item.sheep.get_gender_display(),
                        "weight": float(order_item.sheep.current_weight),
                        "price": float(order_item.price),
                    },
                }
            )
        return result

    @staticmethod
    def update_order_status(token, order_id, status, logistics_info=None):
        breeder = CommerceService._resolve_user(token)
        if breeder.role != 1:
            raise CommerceError("只有养殖户可以更新订单状态。", code=403, http_status=403)

        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist as exc:
            raise CommerceError("未找到订单", code=404, http_status=404) from exc

        order_items = list(order.items.select_related("sheep").all())
        breeder_sheep_ids = set(Sheep.objects.filter(owner=breeder).values_list("id", flat=True))
        sheep_ids = [item.sheep_id for item in order_items]
        if not any(sheep_id in breeder_sheep_ids for sheep_id in sheep_ids):
            raise CommerceError("你没有权限操作该订单。", code=403, http_status=403)
        if not all(sheep_id in breeder_sheep_ids for sheep_id in sheep_ids):
            raise CommerceError(
                "该订单包含其他养殖户的羊只，需由管理员统一处理。",
                code=403,
                http_status=403,
            )

        valid_statuses = [
            "paid",
            "adopting",
            "ready_to_ship",
            "settlement_pending",
            "awaiting_delivery",
            "shipping",
            "completed",
            "cancelled",
        ]
        if status not in valid_statuses:
            raise CommerceError(f"订单状态不合法，可选值：{', '.join(valid_statuses)}")

        CommerceService._validate_order_transition(order, status, logistics_info)
        order.status = status
        if status == "shipping":
            logistics_info = logistics_info or {}
            delivery_method = (logistics_info.get("delivery_method") or "logistics").strip()
            order.delivery_method = delivery_method
            if delivery_method == "logistics":
                order.logistics_company = (logistics_info.get("logistics_company") or "").strip()
                order.logistics_tracking_number = (logistics_info.get("logistics_tracking_number") or "").strip()
                order.offline_delivery_location = ""
                order.offline_delivery_note = ""
            else:
                order.logistics_company = ""
                order.logistics_tracking_number = ""
                order.offline_delivery_location = (logistics_info.get("offline_delivery_location") or "").strip()
                order.offline_delivery_note = (logistics_info.get("offline_delivery_note") or "").strip()
            order.shipping_date = timezone.now()
        elif status == "completed" and not order.delivery_date:
            order.delivery_date = timezone.now()
        order.save()
        return CommerceService._build_order(order)

    @staticmethod
    def _validate_checkout_fields(receiver_name, receiver_phone, shipping_address):
        receiver_name = (receiver_name or "").strip()
        receiver_phone = (receiver_phone or "").strip()
        shipping_address = (shipping_address or "").strip()
        if not receiver_name:
            raise CommerceError("请填写收货人姓名。")
        if not receiver_phone:
            raise CommerceError("请填写联系电话。")
        return receiver_name, receiver_phone, shipping_address

    @staticmethod
    def _calculate_care_fee(order, end_time=None):
        start_time = order.adoption_start_time or order.pay_time or order.created_at
        if not start_time:
            return 0, Decimal("0.00")

        end_time = end_time or order.end_requested_at or timezone.now()
        if end_time <= start_time:
            days = 1
        else:
            seconds = Decimal(str((end_time - start_time).total_seconds()))
            days = int((seconds / Decimal("86400")).to_integral_value(rounding=ROUND_CEILING))
            days = max(days, 1)

        daily_fee = order.daily_care_fee or CommerceService.DEFAULT_DAILY_CARE_FEE
        sheep_count = order.items.count() if order.pk else 1
        sheep_count = max(sheep_count, 1)
        amount = (Decimal(days) * daily_fee * Decimal(sheep_count)).quantize(Decimal("0.01"))
        return days, amount

    @staticmethod
    def _resolve_sheep_daily_care_fee(sheep):
        return Decimal(str(sheep.effective_daily_care_fee))

    @staticmethod
    def _resolve_order_daily_care_fee(cart_items):
        fees = [CommerceService._resolve_sheep_daily_care_fee(item.sheep) for item in cart_items]
        if not fees:
            return CommerceService.DEFAULT_DAILY_CARE_FEE
        average_fee = sum(fees, Decimal("0")) / Decimal(len(fees))
        return average_fee.quantize(Decimal("0.01"))

    @staticmethod
    def _has_active_adoption(sheep_id, exclude_user_id=None):
        qs = OrderItem.objects.filter(
            sheep_id=sheep_id,
            order__status__in=CommerceService.ADOPTED_ORDER_STATUSES,
        )
        if exclude_user_id:
            qs = qs.exclude(order__user_id=exclude_user_id)
        return qs.exists()

    @staticmethod
    def _normalize_cart_item_ids(selected_cart_item_ids):
        if not selected_cart_item_ids:
            return []
        if not isinstance(selected_cart_item_ids, (list, tuple)):
            raise CommerceError("已选购物车项参数格式不正确。")
        normalized = []
        for item_id in selected_cart_item_ids:
            try:
                normalized.append(int(item_id))
            except (TypeError, ValueError) as exc:
                raise CommerceError("已选购物车项中包含无效值。") from exc
        return list(dict.fromkeys(normalized))

    @staticmethod
    def _get_active_cart_reservation(sheep_id, exclude_user_id=None):
        cutoff = timezone.now() - timedelta(minutes=CommerceService.CART_RESERVATION_MINUTES)
        qs = CartItem.objects.filter(sheep_id=sheep_id, updated_at__gte=cutoff).select_related("user")
        if exclude_user_id:
            qs = qs.exclude(user_id=exclude_user_id)
        return qs.order_by("-updated_at").first()

    @staticmethod
    def _assert_cart_items_available(user, cart_items):
        sheep_ids = [item.sheep_id for item in cart_items]
        Sheep.objects.select_for_update().filter(id__in=sheep_ids)
        occupied = (
            OrderItem.objects.select_related("order", "sheep")
            .filter(sheep_id__in=sheep_ids, order__status__in=CommerceService.ADOPTED_ORDER_STATUSES)
            .first()
        )
        if occupied:
            ear_tag = occupied.sheep.ear_tag or f"#{occupied.sheep_id}"
            raise CommerceError(f"羊只 {ear_tag} 已被领养。")

        for item in cart_items:
            reserved_item = CommerceService._get_active_cart_reservation(item.sheep_id, exclude_user_id=user.id)
            if reserved_item:
                raise CommerceError("你选中的羊只里有一部分已被其他用户暂时锁定。")

    @staticmethod
    def _validate_order_transition(order, target_status, logistics_info=None):
        if target_status not in dict(CommerceService.ORDER_STATUS_DISPLAY):
            raise CommerceError("订单状态不合法。")
        allowed = CommerceService.ORDER_TRANSITIONS.get(order.status, [])
        if target_status == order.status:
            return
        if target_status not in allowed:
            current_status = CommerceService.ORDER_STATUS_DISPLAY.get(order.status, order.status)
            next_status = CommerceService.ORDER_STATUS_DISPLAY.get(target_status, target_status)
            raise CommerceError(f"订单状态不能从“{current_status}”流转到“{next_status}”。")
        if target_status == "shipping":
            logistics_info = logistics_info or {}
            delivery_method = (logistics_info.get("delivery_method") or "logistics").strip()
            if delivery_method not in CommerceService.DELIVERY_METHOD_DISPLAY:
                raise CommerceError("交付方式不合法。")
            if delivery_method == "logistics":
                company = (logistics_info.get("logistics_company") or "").strip()
                tracking_number = (logistics_info.get("logistics_tracking_number") or "").strip()
                if not company or not tracking_number:
                    raise CommerceError("物流配送时必须填写物流公司和物流单号。")
            elif not (logistics_info.get("offline_delivery_location") or "").strip():
                raise CommerceError("线下交付时请填写交付地点。")

    @staticmethod
    def _resolve_user(token):
        try:
            return UserService.get_user_by_token(token)
        except UserError as exc:
            raise CommerceError(exc.message, code=exc.code, http_status=exc.http_status) from exc

    @staticmethod
    def _build_cart_item(item):
        sheep = item.sheep
        return {
            "id": item.id,
            "sheep_id": sheep.id,
            "sheep": {
                "id": sheep.id,
                "ear_tag": sheep.ear_tag,
                "gender": sheep.get_gender_display(),
                "weight": float(sheep.current_weight),
                "height": float(sheep.current_height),
                "length": float(sheep.current_length),
                "price": float(sheep.price),
                "daily_care_fee": float(sheep.effective_daily_care_fee),
                "image": sheep.image.url if sheep.image else "",
                "owner_id": sheep.owner_id,
            },
            "quantity": item.quantity,
            "price": float(item.price),
            "daily_care_fee": float(sheep.effective_daily_care_fee),
            "reservation_expires_at": (
                item.updated_at + timedelta(minutes=CommerceService.CART_RESERVATION_MINUTES)
            ).strftime("%Y-%m-%d %H:%M:%S")
            if item.updated_at
            else "",
            "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else "",
        }

    @staticmethod
    def _build_order(order):
        items = order.items.select_related("sheep__owner").all()
        adoption_days, estimated_care_fee = CommerceService._calculate_care_fee(order)
        return {
            "id": order.id,
            "order_no": order.order_no,
            "total_amount": float(order.total_amount),
            "final_amount": float((order.total_amount or Decimal("0")) + (order.care_fee_amount or Decimal("0"))),
            "daily_care_fee": float(order.daily_care_fee or 0),
            "care_fee_amount": float(order.care_fee_amount or 0),
            "estimated_care_fee": float(estimated_care_fee),
            "adoption_days": adoption_days,
            "adoption_start_time": order.adoption_start_time.strftime("%Y-%m-%d %H:%M:%S")
            if order.adoption_start_time
            else "",
            "end_requested_at": order.end_requested_at.strftime("%Y-%m-%d %H:%M:%S")
            if order.end_requested_at
            else "",
            "care_fee_paid_at": order.care_fee_paid_at.strftime("%Y-%m-%d %H:%M:%S")
            if order.care_fee_paid_at
            else "",
            "status": order.status,
            "status_display": CommerceService.ORDER_STATUS_DISPLAY.get(order.status, order.status),
            "pay_time": order.pay_time.strftime("%Y-%m-%d %H:%M:%S") if order.pay_time else "",
            "shipping_date": order.shipping_date.strftime("%Y-%m-%d %H:%M:%S") if order.shipping_date else "",
            "delivery_date": order.delivery_date.strftime("%Y-%m-%d %H:%M:%S") if order.delivery_date else "",
            "delivery_method": order.delivery_method or "logistics",
            "delivery_method_display": CommerceService.DELIVERY_METHOD_DISPLAY.get(
                order.delivery_method or "logistics",
                "物流配送",
            ),
            "logistics_company": order.logistics_company or "",
            "logistics_tracking_number": order.logistics_tracking_number or "",
            "offline_delivery_location": order.offline_delivery_location or "",
            "offline_delivery_note": order.offline_delivery_note or "",
            "receiver_name": order.receiver_name or "",
            "receiver_phone": order.receiver_phone or "",
            "shipping_address": order.shipping_address or "",
            "user_balance": float(order.user.balance),
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S") if order.created_at else "",
            "items": [
                {
                    "sheep_id": item.sheep.id,
                    "ear_tag": item.sheep.ear_tag,
                    "gender": item.sheep.get_gender_display(),
                    "weight": float(item.sheep.current_weight),
                    "health_status": item.sheep.health_status,
                    "price": float(item.price),
                    "breeder_id": item.sheep.owner_id,
                    "breeder_name": item.sheep.owner.nickname or item.sheep.owner.username
                    if item.sheep.owner
                    else "",
                    "breeder_mobile": item.sheep.owner.mobile if item.sheep.owner else "",
                    "farm_name": item.sheep.farm_name or "",
                }
                for item in items
            ],
        }
