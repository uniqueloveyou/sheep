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


import qrcode
from io import BytesIO
from django.core.files import File
import os


def generate_qr_code(sheep):
    """
    为羊只生成二维码并保存到 qr_code 字段

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

    filename = f'sheep_{sheep.id}_{sheep.ear_tag}.png'

    # 删除旧二维码文件（如果存在）
    if sheep.qr_code:
        try:
            if os.path.isfile(sheep.qr_code.path):
                os.remove(sheep.qr_code.path)
        except Exception as e:
            print(f"删除旧二维码失败: {e}")

    # save=False 避免触发再次信号，用 save_base 只更新 qr_code 字段
    from django.core.files.base import ContentFile
    # save=False 避免触发保存
    sheep.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
    # 使用标准的 save 方法
    sheep.save(update_fields=['qr_code'])