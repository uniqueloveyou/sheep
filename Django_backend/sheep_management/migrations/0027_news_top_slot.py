from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sheep_management", "0026_news"),
    ]

    operations = [
        migrations.AddField(
            model_name="news",
            name="top_slot",
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[(1, "首页第1条"), (2, "首页第2条"), (3, "首页第3条")],
                null=True,
                verbose_name="首页推荐位",
            ),
        ),
        migrations.AlterModelOptions(
            name="news",
            options={
                "db_table": "news",
                "ordering": ["top_slot", "-published_at", "-id"],
                "verbose_name": "资讯",
                "verbose_name_plural": "资讯",
            },
        ),
    ]
