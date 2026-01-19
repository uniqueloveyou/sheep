"""
工具函数
"""
import jwt
import datetime
from django.conf import settings

# JWT密钥（应该从settings中读取，这里先用默认值）
SECRET_KEY = getattr(settings, 'SECRET_KEY', 'django-insecure-g!(8vj_8qpxkp9q#_9573#h@b#jgiyiyrlh1+g@am933xm@hd6')


def generate_token(user_id, username=None, expires_in=7*24*3600):
    """
    生成JWT token
    
    Args:
        user_id: 用户ID
        username: 用户名（可选）
        expires_in: 过期时间（秒），默认7天
    
    Returns:
        str: JWT token
    """
    payload = {
        'user_id': user_id,
        'username': username or '',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def verify_token(token):
    """
    验证JWT token
    
    Args:
        token: JWT token字符串
    
    Returns:
        dict: token payload，如果无效返回None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

