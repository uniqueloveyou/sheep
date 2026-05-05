from django.db import models
from .user import User


class Withdrawal(models.Model):
    """养殖户提现申请表"""
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]

    breeder = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='withdrawals',
        limit_choices_to={'role': 1},
        verbose_name='养殖户',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='提现金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')

    # 收款信息
    bank_name = models.CharField(max_length=100, verbose_name='银行名称')
    bank_card_no = models.CharField(max_length=50, verbose_name='银行卡号')
    account_holder = models.CharField(max_length=50, verbose_name='开户人姓名')

    # 审核信息
    remark = models.TextField(null=True, blank=True, verbose_name='备注/拒绝原因')
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_withdrawals',
        verbose_name='审核人',
    )
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='审核时间')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')

    class Meta:
        db_table = 'withdrawals'
        verbose_name = '提现申请'
        verbose_name_plural = '提现申请'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.breeder} - ¥{self.amount} - {self.get_status_display()}"
