from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sheep_management", "0031_order_delivery_method"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="default_daily_care_fee",
            field=models.DecimalField(
                decimal_places=2,
                default=10.0,
                max_digits=10,
                verbose_name="默认每日基础照料费",
            ),
        ),
        migrations.AddField(
            model_name="sheep",
            name="daily_care_fee",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name="每日基础照料费",
            ),
        ),
    ]
