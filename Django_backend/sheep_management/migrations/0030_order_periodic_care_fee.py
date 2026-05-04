from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sheep_management", "0029_faq_models_and_qalog_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="adoption_start_time",
            field=models.DateTimeField(blank=True, null=True, verbose_name="认养开始时间"),
        ),
        migrations.AddField(
            model_name="order",
            name="end_requested_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="申请结束认养时间"),
        ),
        migrations.AddField(
            model_name="order",
            name="daily_care_fee",
            field=models.DecimalField(decimal_places=2, default=10.0, max_digits=10, verbose_name="每日养殖服务费"),
        ),
        migrations.AddField(
            model_name="order",
            name="care_fee_amount",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name="周期服务费"),
        ),
        migrations.AddField(
            model_name="order",
            name="care_fee_paid_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="周期服务费支付时间"),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "待支付"),
                    ("paid", "认养中"),
                    ("adopting", "认养中"),
                    ("ready_to_ship", "认养中"),
                    ("settlement_pending", "待结算"),
                    ("awaiting_delivery", "待交付"),
                    ("shipping", "交付中"),
                    ("completed", "已完成"),
                    ("cancelled", "已取消"),
                ],
                default="pending",
                max_length=20,
                verbose_name="订单状态",
            ),
        ),
    ]
