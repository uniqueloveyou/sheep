from django.db import models


class News(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "草稿"),
        (STATUS_PUBLISHED, "已发布"),
    ]
    TOP_SLOT_CHOICES = [
        (1, "首页第1条"),
        (2, "首页第2条"),
        (3, "首页第3条"),
    ]

    title = models.CharField(max_length=200, verbose_name="标题")
    summary = models.CharField(max_length=500, verbose_name="摘要")
    cover = models.CharField(max_length=500, verbose_name="封面图")
    content = models.TextField(verbose_name="正文")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name="状态",
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="发布时间",
    )
    top_slot = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=TOP_SLOT_CHOICES,
        verbose_name="首页推荐位",
    )

    class Meta:
        db_table = "news"
        verbose_name = "资讯"
        verbose_name_plural = "资讯"
        ordering = ["top_slot", "-published_at", "-id"]

    def __str__(self):
        return self.title
