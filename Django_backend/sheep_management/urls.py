from django.urls import path
from . import views  # 传统视图 + 其余 API（后续逐步迁移）
from .api import auth_api  # 认证 API（已重构）
from .api import user_api  # 用户 API

urlpatterns = [
    # ==========================
    # 认证接口（已迁移到 api/auth_api.py）
    # ==========================

    # 1. 手机号一键登录
    path('api/auth/login_by_phone', auth_api.api_login_by_phone, name='api_login_by_phone'),

    # 2. 微信静默登录
    path('api/auth/login', auth_api.api_login_wx, name='api_login_wx'),
    
    # 3. 用户名密码登录
    path('api/auth/login_password', auth_api.api_login, name='api_login_password'),

    # 4. 用户注册
    path('api/auth/register', auth_api.api_register, name='api_register'),

    # Token 验证
    path('api/auth/check_token', auth_api.api_check_token, name='api_check_token_new'),
    path('check_token', auth_api.api_check_token, name='api_check_token'),

    # ==========================
    # 用户接口（api/user_api.py）
    # ==========================
    path('api/user/info', user_api.api_user_info, name='api_user_info'),
    path('api/user/avatar/upload-url', user_api.api_get_avatar_upload_url, name='api_get_avatar_upload_url'),
    path('api/user/avatar/confirm', user_api.api_confirm_avatar, name='api_confirm_avatar'),
    path('api/user/profile', user_api.api_get_profile, name='api_get_profile'),
    path('api/user/profile_update', user_api.api_update_profile, name='api_update_profile'),
    path('api/user/apply_breeder', user_api.api_apply_breeder, name='api_apply_breeder'),

    # ==========================
    # 其他业务接口
    # ==========================
    path('', views.index, name='index'),

    # 羊只API
    path('api/sheep/search', views.api_search_sheep, name='api_search_sheep'),
    path('search_sheep', views.api_search_sheep, name='search_sheep_compat'),
    path('api/sheep/<int:sheep_id>', views.api_get_sheep_by_id, name='api_get_sheep_by_id'),
    path('search_sheep_by_id', views.api_get_sheep_by_id, name='search_sheep_by_id_compat'),

    # 疫苗记录API
    path('api/vaccine/records/<int:sheep_id>', views.api_get_vaccine_records, name='api_get_vaccine_records'),
    path('vaccine_records/<int:sheep_id>', views.api_get_vaccine_records, name='vaccine_records_compat'),

    # 养殖户API
    path('api/breeders', views.api_get_breeders, name='api_get_breeders'),
    path('api/breeders/<int:breeder_id>', views.api_get_breeders, name='api_get_breeder_detail'),
    path('breeders', views.api_get_breeders, name='breeders_compat'),
    path('breeders/<int:breeder_id>', views.api_get_breeders, name='breeders_detail_compat'),

    # 商品搜索
    path('search_goods', views.api_search_goods, name='api_search_goods'),

    # 生长记录
    path('api/growth/sheep/<int:sheep_id>', views.api_get_sheep_with_growth, name='api_get_sheep_with_growth'),

    # 智能问答
    path('api/qa/ask', views.api_qa_ask, name='api_qa_ask'),
    
    # 溯源查询（通过耳标编号）
    path('api/sheep/trace', views.api_get_sheep_by_ear_tag, name='api_get_sheep_by_ear_tag'),
]