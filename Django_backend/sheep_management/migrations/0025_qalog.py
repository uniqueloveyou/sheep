from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sheep_management', '0024_monitordevice'),
    ]

    operations = [
        migrations.CreateModel(
            name='QALog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_role', models.IntegerField(blank=True, null=True, verbose_name='用户角色')),
                ('question', models.TextField(verbose_name='问题')),
                ('question_type', models.CharField(choices=[('personal', '个人数据类'), ('general', '通用知识类')], default='general', max_length=20, verbose_name='问题类型')),
                ('answer', models.TextField(blank=True, verbose_name='回答')),
                ('success', models.BooleanField(default=True, verbose_name='是否成功')),
                ('fallback_used', models.BooleanField(default=False, verbose_name='是否触发兜底')),
                ('response_time_ms', models.IntegerField(default=0, verbose_name='响应耗时(ms)')),
                ('source_type', models.CharField(choices=[('user_data', '用户数据'), ('general', '通用知识')], default='general', max_length=20, verbose_name='数据来源类型')),
                ('error_message', models.CharField(blank=True, max_length=500, verbose_name='错误信息')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='qa_logs', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '问答日志',
                'verbose_name_plural': '问答日志',
                'db_table': 'qa_logs',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['-created_at'], name='qa_logs_created_50cd7e_idx'),
                    models.Index(fields=['question_type', '-created_at'], name='qa_logs_questio_80ff8f_idx'),
                    models.Index(fields=['success', '-created_at'], name='qa_logs_success_4fa7d6_idx'),
                    models.Index(fields=['fallback_used', '-created_at'], name='qa_logs_fallbac_0343f1_idx'),
                ],
            },
        ),
    ]
