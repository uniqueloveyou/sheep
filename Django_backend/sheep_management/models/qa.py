from django.db import models

from .user import User


class QALog(models.Model):
    """智能问答日志"""

    QUESTION_TYPE_CHOICES = [
        ('personal', '个人数据类'),
        ('general', '通用知识类'),
    ]

    SOURCE_TYPE_CHOICES = [
        ('user_data', '用户数据'),
        ('general', '通用知识'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qa_logs',
        verbose_name='用户',
    )
    user_role = models.IntegerField(null=True, blank=True, verbose_name='用户角色')
    question = models.TextField(verbose_name='问题')
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default='general',
        verbose_name='问题类型',
    )
    answer = models.TextField(blank=True, verbose_name='回答')
    success = models.BooleanField(default=True, verbose_name='是否成功')
    fallback_used = models.BooleanField(default=False, verbose_name='是否触发兜底')
    response_time_ms = models.IntegerField(default=0, verbose_name='响应耗时(ms)')
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        default='general',
        verbose_name='数据来源类型',
    )
    error_message = models.CharField(max_length=500, blank=True, verbose_name='错误信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'qa_logs'
        verbose_name = '问答日志'
        verbose_name_plural = '问答日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['question_type', '-created_at']),
            models.Index(fields=['success', '-created_at']),
            models.Index(fields=['fallback_used', '-created_at']),
        ]

    def __str__(self):
        q = (self.question or '')[:30]
        return f'{q}...'
