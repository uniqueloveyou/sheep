from django.db import models


class QACategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='问答分类名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='问答分类编码')
    description = models.CharField(max_length=255, blank=True, verbose_name='分类说明')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    status = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'qa_category'
        verbose_name = '问答分类'
        verbose_name_plural = '问答分类'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class QAPair(models.Model):
    ANSWER_TYPE_CHOICES = [
        ('text', '纯文本'),
        ('table', '表格型'),
        ('mixed', '混合型'),
    ]

    category = models.ForeignKey(
        QACategory,
        on_delete=models.CASCADE,
        related_name='qa_pairs',
        verbose_name='所属分类',
    )
    question = models.CharField(max_length=255, unique=True, verbose_name='标准问题')
    answer = models.TextField(verbose_name='标准答案')
    answer_type = models.CharField(
        max_length=20,
        choices=ANSWER_TYPE_CHOICES,
        default='text',
        verbose_name='答案类型',
    )
    keywords = models.CharField(max_length=500, blank=True, verbose_name='关键词')
    month_stage = models.CharField(max_length=50, blank=True, verbose_name='适用月龄阶段')
    is_hot = models.BooleanField(default=False, verbose_name='是否热门问题')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    status = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'qa_pair'
        verbose_name = '问答对'
        verbose_name_plural = '问答对'
        ordering = ['sort_order', 'id']
        indexes = [
            models.Index(fields=['status', 'sort_order']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['is_hot', 'status']),
        ]

    def __str__(self):
        return self.question


class QAAlias(models.Model):
    qa_pair = models.ForeignKey(
        QAPair,
        on_delete=models.CASCADE,
        related_name='aliases',
        verbose_name='所属标准问题',
    )
    alias_question = models.CharField(max_length=255, verbose_name='别名问题')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'qa_alias'
        verbose_name = '问答别名'
        verbose_name_plural = '问答别名'
        unique_together = ('qa_pair', 'alias_question')
        indexes = [
            models.Index(fields=['alias_question']),
        ]

    def __str__(self):
        return self.alias_question


class QARelated(models.Model):
    source_qa = models.ForeignKey(
        QAPair,
        on_delete=models.CASCADE,
        related_name='related_sources',
        verbose_name='源问题',
    )
    target_qa = models.ForeignKey(
        QAPair,
        on_delete=models.CASCADE,
        related_name='related_targets',
        verbose_name='关联问题',
    )
    sort_order = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        db_table = 'qa_related'
        verbose_name = '关联问题'
        verbose_name_plural = '关联问题'
        unique_together = ('source_qa', 'target_qa')
        ordering = ['sort_order', 'id']


class QAAnswerDetail(models.Model):
    qa_pair = models.ForeignKey(
        QAPair,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name='所属问题',
    )
    stage_name = models.CharField(max_length=50, verbose_name='阶段名称')
    weight_range = models.CharField(max_length=100, blank=True, verbose_name='体重范围')
    nutrition_value = models.CharField(max_length=255, blank=True, verbose_name='营养说明')
    cost_value = models.CharField(max_length=255, blank=True, verbose_name='成本说明')
    price_value = models.CharField(max_length=255, blank=True, verbose_name='价格说明')
    description = models.TextField(blank=True, verbose_name='补充说明')
    sort_order = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        db_table = 'qa_answer_detail'
        verbose_name = '问答明细'
        verbose_name_plural = '问答明细'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f'{self.qa_pair.question} - {self.stage_name}'
