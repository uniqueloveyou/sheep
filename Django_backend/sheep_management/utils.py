"""
工具函数
"""
import jwt
import datetime
from django.conf import settings

# JWT密钥，来自 Django settings，settings 会从项目根目录 .env 读取。
SECRET_KEY = settings.SECRET_KEY


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


import qrcode
from io import BytesIO
import re


def generate_qr_code(sheep):
    """
    为羊只生成二维码并保存到 Cloudflare R2。

    二维码内容为羊只耳标号，数据库 qr_code 字段只保存 R2 object key，
    例如：qrcodes/sheep_1151_TY0072603060FYY.png。

    Args:
        sheep: Sheep 模型实例（需已保存，有 id）
    """
    if not sheep.ear_tag:
        return

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(sheep.ear_tag)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    safe_ear_tag = re.sub(r'[^A-Za-z0-9_-]+', '_', sheep.ear_tag)
    object_key = f'qrcodes/sheep_{sheep.id}_{safe_ear_tag}.png'
    _upload_qr_code_to_r2(object_key, buffer.getvalue())

    sheep.qr_code.name = object_key
    sheep.save(update_fields=['qr_code'])


def _upload_qr_code_to_r2(object_key, content):
    """Upload QR PNG bytes directly to Cloudflare R2."""
    import boto3

    client = boto3.client(
        's3',
        endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'auto'),
    )
    client.put_object(
        Bucket=settings.R2_BUCKET_NAME,
        Key=object_key,
        Body=content,
        ContentType='image/png',
        CacheControl='max-age=86400',
    )


def get_r2_public_url(object_key):
    """Build public R2 URL for a stored object key."""
    if not object_key:
        return ''
    if str(object_key).startswith(('http://', 'https://')):
        return str(object_key)
    return f"{settings.R2_PUBLIC_URL.rstrip('/')}/{str(object_key).lstrip('/')}"
