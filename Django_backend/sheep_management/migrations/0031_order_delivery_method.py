from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sheep_management", "0030_order_periodic_care_fee"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="delivery_method",
            field=models.CharField(
                choices=[("logistics", "物流配送"), ("offline", "线下交付")],
                default="logistics",
                max_length=20,
                verbose_name="交付方式",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="offline_delivery_location",
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name="线下交付地点"),
        ),
        migrations.AddField(
            model_name="order",
            name="offline_delivery_note",
            field=models.TextField(blank=True, null=True, verbose_name="线下交付说明"),
        ),
    ]
