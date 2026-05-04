"""
认证业务逻辑 Service
所有方法为纯业务逻辑，不依赖任何 HTTP Request/Response 对象。
通过 raise AuthError 传递错误。
"""
import hashlib
import re
import time
import requests as http_requests
from datetime import datetime

from django.conf import settings
from django.db.models import Q

from ..models import User
from ..utils import generate_token, verify_token


class AuthError(Exception):
    """认证业务异常"""
    def __init__(self, message, code=400, http_status=400):
        self.message = message
        self.code = code          # 业务错误码
        self.http_status = http_status  # HTTP 状态码
        super().__init__(self.message)


class AuthService:
    """认证相关业务逻辑"""

    # ========================
    #  公开方法
    # ========================

    @staticmethod
    def login_by_phone(code, phone_code):
        """
        微信手机号一键登录
        :param code: wx.login() 返回的 code，用于换取 openid
        :param phone_code: getPhoneNumber 返回的 code，用于解密手机号
        :return: dict（token + userInfo）
        """
        if not code or not phone_code:
            raise AuthError('参数缺失：code 和 phoneCode 不能为空')

        # 1. 获取手机号
        pure_phone = AuthService._get_wx_phone(phone_code)

        # 2. 获取 openid
        wx_data = AuthService._get_wx_openid(code)
        openid = wx_data.get('openid')

        # 3. 查找或创建用户
        user = AuthService._find_or_create_user(
            openid=openid,
            mobile=pure_phone,
            nickname_prefix='用户',
            nickname_key=pure_phone[-4:] if pure_phone else None,
            username_prefix='wx_',
            username_key=pure_phone[-4:] if pure_phone else None,
        )

        # 4. 生成 token 并返回
        token = generate_token(user.id, user.username)
        return {
            'token': token,
            'uid': user.id,
            'username': user.username,
            'mobile': user.mobile or '',
            'openid': user.openid or '',
            'userInfo': AuthService._build_user_info(user),
        }

    @staticmethod
    def login_by_wx_code(code):
        """
        微信静默登录（仅 code 换 openid，无手机号）
        :param code: wx.login() 返回的 code
        :return: dict
        """
        if not code:
            raise AuthError('参数缺失：缺少 code')

        # 1. 获取 openid
        wx_data = AuthService._get_wx_openid(code)
        openid = wx_data.get('openid')
        unionid = wx_data.get('unionid')

        if not openid:
            raise AuthError('无法获取用户 OpenID', code=401, http_status=401)

        # 2. 查找或创建用户
        user = User.objects.filter(openid=openid).first()

        if not user:
            try:
                user = User.objects.create(
                    username=f"wx_{openid[-8:]}",
                    openid=openid,
                    unionid=unionid or None,
                    nickname=f"微信用户{openid[-4:]}",
                    last_login=datetime.now(),
                )
                user.set_unusable_password()
                user.save()
            except Exception:
                user = User.objects.filter(openid=openid).first()
                if not user:
                    raise AuthError('创建用户失败', code=500, http_status=500)
        else:
            if unionid and not user.unionid:
                user.unionid = unionid
            user.last_login = datetime.now()
            user.save()

        # 3. 生成 token 并返回
        token = generate_token(user.id, user.username)
        return {
            'token': token,
            'openid': user.openid,
            'userInfo': AuthService._build_user_info(user),
        }

    @staticmethod
    def login_by_password(username, password):
        """
        用户名/手机号 + 密码登录
        :return: dict
        """
        if not username or not password:
            raise AuthError('用户名和密码不能为空')

        user = User.objects.filter(
            Q(username=username) | Q(mobile=username)
        ).first()

        if not user:
            raise AuthError('用户名或密码错误', code=401, http_status=401)

        # 兼容：如果是旧的明文密码，先尝试 check_password
        if user.has_usable_password():
            if not user.check_password(password):
                # 降级：兼容老的明文密码
                if user.password != password:
                    raise AuthError('用户名或密码错误', code=401, http_status=401)
                # 明文匹配成功，升级为哈希存储
                user.set_password(password)
        else:
            raise AuthError('该账号未设置密码，请使用微信登录', code=401, http_status=401)

        user.last_login = datetime.now()
        user.save()

        token = generate_token(user.id, user.username)
        return {
            'token': token,
            'uid': user.id,
            'username': user.username,
            'nickname': user.nickname or '',
            'openid': user.openid or '',
            'mobile': user.mobile or '',
        }

    @staticmethod
    def register(username, password, mobile=None, nickname=None):
        """
        用户名密码注册
        :return: dict
        """
        # 参数校验
        if not username:
            raise AuthError('用户名不能为空')
        if not password:
            raise AuthError('密码不能为空')
        if len(username) < 3 or len(username) > 50:
            raise AuthError('用户名长度为3-50个字符')
        if len(password) < 6:
            raise AuthError('密码长度至少6个字符')
        mobile = (mobile or '').strip()
        if mobile and not re.fullmatch(r'1[3-9]\d{9}', mobile):
            raise AuthError('手机号格式不正确')

        # 唯一性检查
        if User.objects.filter(username=username).exists():
            raise AuthError('用户名已存在', code=409, http_status=409)
        if mobile and User.objects.filter(mobile=mobile).exists():
            raise AuthError('手机号已被注册', code=409, http_status=409)

        # 生成临时 openid
        temp_openid = hashlib.md5(f"{username}_{time.time()}".encode()).hexdigest()

        # 创建用户（使用 set_password 安全存储）
        user = User(
            username=username,
            mobile=mobile or None,
            nickname=nickname or username,
            openid=temp_openid,
        )
        user.set_password(password)
        user.save()

        token = generate_token(user.id, user.username)
        return {
            'token': token,
            'uid': user.id,
            'username': user.username,
            'nickname': user.nickname or '',
            'mobile': user.mobile or '',
            'userInfo': AuthService._build_user_info(user),
        }

    @staticmethod
    def check_token(token):
        """
        验证 JWT Token
        :return: dict（用户信息）
        """
        if not token:
            raise AuthError('缺少 token 参数')

        payload = verify_token(token)
        if not payload:
            raise AuthError('token 无效或已过期', code=401, http_status=401)

        user_id = payload.get('user_id')
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise AuthError('用户不存在', code=404, http_status=404)

        return {
            'uid': user.id,
            'username': user.username or '',
            'nickname': user.nickname or '',
            'openid': user.openid or '',
            'mobile': user.mobile or '',
        }

    @staticmethod
    def get_user_by_token(token):
        """
        通过 JWT Token 获取用户对象。
        保留这个入口是为了兼容羊只维护等旧 API 中对 AuthService 的调用。
        """
        if not token:
            raise AuthError('缺少 token 参数', code=401, http_status=401)

        payload = verify_token(token)
        if not payload:
            raise AuthError('token 无效或已过期', code=401, http_status=401)

        user_id = payload.get('user_id')
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise AuthError('用户不存在', code=404, http_status=404)

    # ========================
    #  私有方法
    # ========================

    @staticmethod
    def _get_wx_openid(code):
        """调用微信 jscode2session 接口换取 openid"""
        app_id = settings.WX_APP_ID
        app_secret = settings.WX_APP_SECRET
        url = (
            f"https://api.weixin.qq.com/sns/jscode2session"
            f"?appid={app_id}&secret={app_secret}"
            f"&js_code={code}&grant_type=authorization_code"
        )
        res = http_requests.get(url).json()
        if res.get('errcode'):
            raise AuthError(
                f"微信登录失败: {res.get('errmsg', '未知错误')}",
                code=401, http_status=401
            )
        return res

    @staticmethod
    def _get_wx_phone(phone_code):
        """获取微信 access_token → 解密手机号"""
        app_id = settings.WX_APP_ID
        app_secret = settings.WX_APP_SECRET

        # 1. 获取 access_token
        token_url = (
            f"https://api.weixin.qq.com/cgi-bin/token"
            f"?grant_type=client_credential&appid={app_id}&secret={app_secret}"
        )
        token_res = http_requests.get(token_url).json()
        access_token = token_res.get('access_token')
        if not access_token:
            raise AuthError('后端配置错误: AccessToken 获取失败', code=500, http_status=500)

        # 2. 解密手机号
        phone_url = f"https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={access_token}"
        phone_res = http_requests.post(phone_url, json={"code": phone_code}).json()
        if phone_res.get('errcode') != 0:
            raise AuthError('手机号授权失败', code=401, http_status=401)

        return phone_res.get('phone_info', {}).get('purePhoneNumber')

    @staticmethod
    def _find_or_create_user(openid=None, mobile=None, unionid=None,
                              nickname_prefix='用户', nickname_key=None,
                              username_prefix='wx_', username_key=None):
        """
        统一的查找或创建用户逻辑
        查找优先级: 手机号 → openid
        """
        user = None

        # 先通过手机号查找
        if mobile:
            user = User.objects.filter(mobile=mobile).first()
        # 再通过 openid 查找
        if not user and openid:
            user = User.objects.filter(openid=openid).first()

        if not user:
            # 自动注册
            if not openid and mobile:
                openid = f"phone_{mobile}"

            try:
                user = User.objects.create(
                    username=f"{username_prefix}{username_key or (openid[-8:] if openid else 'unknown')}",
                    mobile=mobile,
                    openid=openid,
                    unionid=unionid,
                    nickname=f"{nickname_prefix}{nickname_key or (openid[-4:] if openid else '')}",
                    last_login=datetime.now(),
                )
                user.set_unusable_password()
                user.save()
            except Exception:
                # 唯一性冲突时重试查找
                if openid:
                    user = User.objects.filter(openid=openid).first()
                if not user and mobile:
                    user = User.objects.filter(mobile=mobile).first()
                if not user:
                    raise AuthError('创建用户失败', code=500, http_status=500)
        else:
            # 更新现有信息
            changed = False
            if openid and not user.openid:
                user.openid = openid
                changed = True
            if mobile and not user.mobile:
                user.mobile = mobile
                changed = True
            if unionid and not user.unionid:
                user.unionid = unionid
                changed = True
            user.last_login = datetime.now()
            user.save()

        return user

    @staticmethod
    def _build_user_info(user):
        """统一构建前端 userInfo 结构"""
        return {
            'id': user.id,
            'role': user.role,
            'username': user.username or '',
            'nickname': user.nickname or '',
            'mobile': user.mobile or '',
            'avatar_url': user.avatar_url or '',
        }
