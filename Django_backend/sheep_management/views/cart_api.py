"""购物车API接口视图"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from ..models import User, Sheep, CartItem
from ..utils import verify_token


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_cart(request):
    """
    购物车接口
    GET /api/cart - 获取购物车列表（需要token）
    POST /api/cart - 添加商品到购物车（需要token）
    """
    try:
        # 从请求头或参数中获取token
        token = request.headers.get('Authorization', '').replace('Bearer ', '') or request.GET.get('token', '')
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                token = data.get('token', '') or token
            except:
                pass
        
        if not token:
            return JsonResponse({
                'code': 401,
                'msg': '缺少token参数',
                'data': None
            }, status=401)
        
        # 验证token
        payload = verify_token(token)
        if not payload:
            return JsonResponse({
                'code': 401,
                'msg': 'token无效或已过期',
                'data': None
            }, status=401)
        
        user_id = payload.get('user_id')
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'code': 404,
                'msg': '用户不存在',
                'data': None
            }, status=404)
        
        if request.method == 'GET':
            # 获取购物车列表
            cart_items = CartItem.objects.filter(user=user).select_related('sheep')
            result = []
            for item in cart_items:
                result.append({
                    'id': item.id,
                    'sheep_id': item.sheep.id,
                    'sheep': {
                        'id': item.sheep.id,
                        'gender': item.sheep.gender,
                        'weight': float(item.sheep.weight),
                        'height': float(item.sheep.height),
                        'length': float(item.sheep.length)
                    },
                    'quantity': item.quantity,
                    'price': float(item.price),
                    'total_price': float(item.price * item.quantity),
                    'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            return JsonResponse(result, safe=False, status=200)
        
        elif request.method == 'POST':
            # 添加商品到购物车
            try:
                data = json.loads(request.body)
            except:
                data = {}
            
            sheep_id = data.get('sheep_id') or data.get('sheepId')
            quantity = int(data.get('quantity', 1))
            price = float(data.get('price', 0))
            
            if not sheep_id:
                return JsonResponse({
                    'code': 400,
                    'msg': '缺少羊只ID参数',
                    'data': None
                }, status=400)
            
            try:
                sheep = Sheep.objects.get(pk=sheep_id)
            except Sheep.DoesNotExist:
                return JsonResponse({
                    'code': 404,
                    'msg': '羊只不存在',
                    'data': None
                }, status=404)
            
            # 如果价格未提供，根据体重计算（体重*10）
            if price == 0:
                price = float(sheep.weight) * 10
            
            # 检查是否已存在
            cart_item, created = CartItem.objects.get_or_create(
                user=user,
                sheep=sheep,
                defaults={'quantity': quantity, 'price': price}
            )
            
            if not created:
                # 已存在，更新数量
                cart_item.quantity += quantity
                cart_item.price = price  # 更新价格
                cart_item.save()
            
            return JsonResponse({
                'code': 0,
                'msg': '添加成功',
                'data': {
                    'id': cart_item.id,
                    'sheep_id': cart_item.sheep.id,
                    'quantity': cart_item.quantity,
                    'price': float(cart_item.price)
                }
            }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'data': None
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE", "PUT"])
def api_cart_item(request, cart_item_id):
    """
    购物车商品操作接口
    DELETE /api/cart/{id} - 删除购物车商品（需要token）
    PUT /api/cart/{id} - 更新购物车商品数量（需要token）
    """
    try:
        # 从请求头或参数中获取token
        token = request.headers.get('Authorization', '').replace('Bearer ', '') or request.GET.get('token', '')
        if request.method == 'PUT':
            try:
                data = json.loads(request.body)
                token = data.get('token', '') or token
            except:
                pass
        
        if not token:
            return JsonResponse({
                'code': 401,
                'msg': '缺少token参数',
                'data': None
            }, status=401)
        
        # 验证token
        payload = verify_token(token)
        if not payload:
            return JsonResponse({
                'code': 401,
                'msg': 'token无效或已过期',
                'data': None
            }, status=401)
        
        user_id = payload.get('user_id')
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'code': 404,
                'msg': '用户不存在',
                'data': None
            }, status=404)
        
        try:
            cart_item = CartItem.objects.get(pk=cart_item_id, user=user)
        except CartItem.DoesNotExist:
            return JsonResponse({
                'code': 404,
                'msg': '购物车商品不存在',
                'data': None
            }, status=404)
        
        if request.method == 'DELETE':
            # 删除购物车商品
            cart_item.delete()
            return JsonResponse({
                'code': 0,
                'msg': '删除成功',
                'data': None
            }, status=200)
        
        elif request.method == 'PUT':
            # 更新购物车商品数量
            try:
                data = json.loads(request.body)
                quantity = int(data.get('quantity', 1))
                if quantity <= 0:
                    cart_item.delete()
                    return JsonResponse({
                        'code': 0,
                        'msg': '已删除',
                        'data': None
                    }, status=200)
                cart_item.quantity = quantity
                cart_item.save()
                return JsonResponse({
                    'code': 0,
                    'msg': '更新成功',
                    'data': {
                        'id': cart_item.id,
                        'quantity': cart_item.quantity,
                        'price': float(cart_item.price),
                        'total_price': float(cart_item.price * cart_item.quantity)
                    }
                }, status=200)
            except Exception as e:
                return JsonResponse({
                    'code': 400,
                    'msg': f'参数错误: {str(e)}',
                    'data': None
                }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'msg': f'服务器错误: {str(e)}',
            'data': None
        }, status=500)

