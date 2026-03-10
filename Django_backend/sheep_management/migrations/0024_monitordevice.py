from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sheep_management', '0023_order_receiver_shipping'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonitorDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='设备名称')),
                ('device_code', models.CharField(max_length=64, unique=True, verbose_name='设备编号')),
                ('stream_url', models.URLField(max_length=500, verbose_name='视频流地址')),
                ('location', models.CharField(blank=True, max_length=200, null=True, verbose_name='安装位置')),
                ('status', models.CharField(choices=[('online', '在线'), ('offline', '离线')], default='offline', max_length=16, verbose_name='在线状态')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('last_heartbeat', models.DateTimeField(blank=True, null=True, verbose_name='最后心跳时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('owner', models.ForeignKey(limit_choices_to={'role': 1}, on_delete=django.db.models.deletion.CASCADE, related_name='monitor_devices', to=settings.AUTH_USER_MODEL, verbose_name='所属养殖户')),
            ],
            options={
                'verbose_name': '监控设备',
                'verbose_name_plural': '监控设备',
                'db_table': 'monitor_devices',
                'ordering': ['-created_at'],
            },
        ),
    ]
