from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sheep_management", "0025_qalog"),
    ]

    operations = [
        migrations.CreateModel(
            name="News",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200, verbose_name="标题")),
                ("summary", models.CharField(max_length=500, verbose_name="摘要")),
                ("cover", models.CharField(max_length=500, verbose_name="封面图")),
                ("content", models.TextField(verbose_name="正文")),
                ("status", models.CharField(choices=[("draft", "草稿"), ("published", "已发布")], default="draft", max_length=20, verbose_name="状态")),
                ("published_at", models.DateTimeField(blank=True, null=True, verbose_name="发布时间")),
            ],
            options={
                "verbose_name": "资讯",
                "verbose_name_plural": "资讯",
                "db_table": "news",
                "ordering": ["-published_at", "-id"],
            },
        ),
    ]
