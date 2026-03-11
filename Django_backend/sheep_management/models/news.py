from django.db import models


class News(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "草稿"),
        (STATUS_PUBLISHED, "已发布"),
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

    class Meta:
        db_table = "news"
        verbose_name = "资讯"
        verbose_name_plural = "资讯"
        ordering = ["-published_at", "-id"]

    def __str__(self):
        return self.title
