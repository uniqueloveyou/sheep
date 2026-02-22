"""
视图模块 - 统一导出所有视图
认证相关 API 已迁移到 api/auth_api.py
羊只相关 API 已迁移到 api/sheep_api.py
"""
from .index import index
from .sheep import sheep_list, sheep_detail, sheep_create, sheep_edit, sheep_delete
from .breeder import breeder_list, breeder_detail, breeder_create, breeder_edit, breeder_delete
from .growth import growth_record_list, growth_record_create
from .feeding import feeding_record_list, feeding_record_create
from .vaccination import vaccination_list, vaccination_create
from .user import user_list, user_detail
from .views import api_get_breeders, api_search_goods
from .cart_api import api_cart, api_cart_item
from .promotion_api import api_promotion_activities, api_promotion_activity_detail, api_coupons, api_claim_coupon
from .qa_api import api_qa_ask

__all__ = [
    'index',
    'sheep_list', 'sheep_detail', 'sheep_create', 'sheep_edit', 'sheep_delete',
    'breeder_list', 'breeder_detail', 'breeder_create', 'breeder_edit', 'breeder_delete',
    'growth_record_list', 'growth_record_create',
    'feeding_record_list', 'feeding_record_create',
    'vaccination_list', 'vaccination_create',
    'user_list', 'user_detail',
    'api_get_breeders',
    'api_search_goods',
    'api_cart',
    'api_cart_item',
    'api_promotion_activities',
    'api_promotion_activity_detail',
    'api_coupons',
    'api_claim_coupon',
    'api_qa_ask',
]


