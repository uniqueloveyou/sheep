from django.db import models


class MonitorDevice(models.Model):
    """Breeder-owned monitor device information."""

    STATUS_ONLINE = 'online'
    STATUS_OFFLINE = 'offline'
    STATUS_CHOICES = [
        (STATUS_ONLINE, '在线'),
        (STATUS_OFFLINE, '离线'),
    ]

    owner = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 1},
        related_name='monitor_devices',
        verbose_name='所属养殖户',
    )
    name = models.CharField(max_length=100, verbose_name='设备名称')
    device_code = models.CharField(max_length=64, unique=True, verbose_name='设备编号')
    stream_url = models.URLField(max_length=500, verbose_name='视频流地址')
    location = models.CharField(max_length=200, null=True, blank=True, verbose_name='安装位置')
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_OFFLINE,
        verbose_name='在线状态',
    )
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    last_heartbeat = models.DateTimeField(null=True, blank=True, verbose_name='最后心跳时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'monitor_devices'
        verbose_name = '监控设备'
        verbose_name_plural = '监控设备'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.device_code} - {self.name}'
