"""优惠券API接口"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
from ..models import Coupon, UserCoupon, User
from ..utils import verify_token


@csrf_exempt
@require_http_methods(["GET"])
def api_coupons(request):
    """
    获取优惠券列表（可领取的优惠券）
    GET /api/promotions/coupons
    参数：
        user_id: 用户ID（可选，如果提供则返回用户已领取的优惠券）
    """
    try:
        user_id = request.GET.get('user_id', '').strip()
        token = request.GET.get('token', '').strip()

        # 优先通过token获取用户
        resolved_user = None
        if token:
            payload = verify_token(token)
            if payload:
                try:
                    resolved_user = User.objects.get(pk=payload.get('user_id'))
                    user_id = str(resolved_user.id)
                except User.DoesNotExist:
                    pass

        if not resolved_user and user_id:
            try:
                resolved_user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                pass
        
        if resolved_user:
            # 返回用户已领取的优惠券
            user_coupons = UserCoupon.objects.filter(user=resolved_user).select_related('coupon')
            result = []
            for uc in user_coupons:
                coupon = uc.coupon
                # 检查是否过期
                if timezone.now() > coupon.valid_until:
                    uc.status = 'expired'
                    uc.save()
                
                owner_info = {
                    'id': coupon.owner.id,
                    'name': coupon.owner.nickname or coupon.owner.username,
                    'farm_name': getattr(coupon.owner, 'farm_name', '')
                } if coupon.owner else None

                result.append({
                    'id': uc.id,
                    'coupon_id': coupon.id,
                    'name': coupon.name,
                    'code': coupon.code,
                    'coupon_type': coupon.coupon_type,
                    'status': uc.status,
                    'owner': owner_info,  # 新增
                    'discount_amount': float(coupon.discount_amount) if coupon.discount_amount else None,
                    'discount_rate': float(coupon.discount_rate) if coupon.discount_rate else None,
                    'min_purchase_amount': float(coupon.min_purchase_amount),
                    'max_discount_amount': float(coupon.max_discount_amount) if coupon.max_discount_amount else None,
                    'valid_from': coupon.valid_from.strftime('%Y-%m-%d %H:%M:%S'),
                    'valid_until': coupon.valid_until.strftime('%Y-%m-%d %H:%M:%S'),
                    'description': coupon.description or '',
                    'obtained_at': uc.obtained_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'used_at': uc.used_at.strftime('%Y-%m-%d %H:%M:%S') if uc.used_at else None,
                })
            
            return JsonResponse({
                'code': 0,
                'msg': '获取成功',
                'data': result
            }, status=200)
        else:
            # 返回可领取的优惠券列表
            now = timezone.now()
            coupons = Coupon.objects.filter(
                status='active',
                valid_from__lte=now,
                valid_until__gte=now
            ).order_by('-created_at')
            
            result = []
            for coupon in coupons:
                # 检查是否还有剩余数量
                if coupon.total_count and coupon.used_count >= coupon.total_count:
                    continue
                
                owner_info = {
                    'id': coupon.owner.id,
                    'name': coupon.owner.nickname or coupon.owner.username,
                    'farm_name': getattr(coupon.owner, 'farm_name', '')
                } if coupon.owner else None

                result.append({
                    'id': coupon.id,
                    'name': coupon.name,
                    'code': coupon.code,
                    'coupon_type': coupon.coupon_type,
                    'status': coupon.status,
                    'owner': owner_info,
                    'discount_amount': float(coupon.discount_amount) if coupon.discount_amount else None,
                    'discount_rate': float(coupon.discount_rate) if coupon.discount_rate else None,
                    'min_purchase_amount': float(coupon.min_purchase_amount),
                    'max_discount_amount': float(coupon.max_discount_amount) if coupon.max_discount_amount else None,
                    'total_count': coupon.total_count,
                    'used_count': coupon.used_count,
                    'remaining_count': (coupon.total_count - coupon.used_count) if coupon.total_count else None,
                    'user_limit': coupon.user_limit,
                    'valid_from': coupon.valid_from.strftime('%Y-%m-%d %H:%M:%S'),
                    'valid_until': coupon.valid_until.strftime('%Y-%m-%d %H:%M:%S'),
                    'description': coupon.description or '',
                })
            
            return JsonResponse({
                'code': 0,
                'msg': '获取成功',
                'data': result
            }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'data': None
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_claim_coupon(request):
    """
    领取优惠券
    POST /api/promotions/coupons/claim
    请求体：
        {
            "token": "xxx",    // JWT token（优先）
            "user_id": 1,      // 或直接传user_id
            "coupon_id": 1
        }
    """
    try:
        data = json.loads(request.body)
        coupon_id = data.get('coupon_id')
        token = data.get('token', '')
        user_id = data.get('user_id')

        if not coupon_id:
            return JsonResponse({
                'code': 400,
                'msg': '优惠券ID不能为空',
                'data': None
            }, status=400)

        # 优先通过token获取用户
        user = None
        if token:
            payload = verify_token(token)
            if payload:
                try:
                    user = User.objects.get(pk=payload.get('user_id'))
                except User.DoesNotExist:
                    pass

        # 回退到user_id
        if not user and user_id:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                pass

        if not user:
            return JsonResponse({
                'code': 401,
                'msg': '用户未登录或不存在',
                'data': None
            }, status=401)
        
        try:
            coupon = Coupon.objects.get(pk=coupon_id)
        except Coupon.DoesNotExist:
            return JsonResponse({
                'code': 404,
                'msg': '优惠券不存在',
                'data': None
            }, status=404)
        
        # 检查优惠券状态
        if coupon.status != 'active':
            return JsonResponse({
                'code': 400,
                'msg': '优惠券不可用',
                'data': None
            }, status=400)
        
        # 检查有效期
        now = timezone.now()
        if now < coupon.valid_from or now > coupon.valid_until:
            return JsonResponse({
                'code': 400,
                'msg': '优惠券不在有效期内',
                'data': None
            }, status=400)
        
        # 检查总数量限制
        if coupon.total_count and coupon.used_count >= coupon.total_count:
            return JsonResponse({
                'code': 400,
                'msg': '优惠券已领完',
                'data': None
            }, status=400)
        
        # 检查用户是否已领取
        user_coupon_count = UserCoupon.objects.filter(user=user, coupon=coupon).count()
        # 养殖户发放的优惠券，每位用户仅可领取一次
        effective_user_limit = 1 if coupon.owner_id else coupon.user_limit
        if user_coupon_count >= effective_user_limit:
            return JsonResponse({
                'code': 400,
                'msg': '每位用户仅可领取一次',
                'data': None
            }, status=400)
        
        # 创建用户优惠券记录
        user_coupon, created = UserCoupon.objects.get_or_create(
            user=user,
            coupon=coupon,
            defaults={'status': 'unused'}
        )
        
        if not created:
            return JsonResponse({
                'code': 400,
                'msg': '每位用户仅可领取一次',
                'data': None
            }, status=400)
        
        # 更新优惠券使用计数
        coupon.used_count += 1
        coupon.save()
        
        return JsonResponse({
            'code': 0,
            'msg': '领取成功',
            'data': {
                'id': user_coupon.id,
                'coupon_id': coupon.id,
                'name': coupon.name,
                'code': coupon.code,
            }
        }, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'code': 400,
            'msg': '请求数据格式错误',
            'data': None
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'data': None
        }, status=500)


