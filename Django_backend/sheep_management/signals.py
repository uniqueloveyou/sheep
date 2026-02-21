from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='sheep_management.Sheep')
def sheep_post_save(sender, instance, created, update_fields, **kwargs):
    """
    Sheep 保存后自动生成二维码
    用 update_fields 判断阻断递归：generate_qr_code 内部用 save_base(update_fields=['qr_code'])
    保存，此时信号会再次触发，但检测到 update_fields 只含 qr_code 就直接返回
    """
    if update_fields and frozenset(update_fields) == frozenset(['qr_code']):
        return

    if instance.ear_tag:
        if created or not instance.qr_code:
            from .utils import generate_qr_code
            generate_qr_code(instance)
