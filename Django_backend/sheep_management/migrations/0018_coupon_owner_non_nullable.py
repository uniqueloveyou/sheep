# Generated manually

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sheep_management', '0017_add_coupon_owner_nullable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='owner',
            field=models.ForeignKey(
                limit_choices_to={'role': 1},
                on_delete=django.db.models.deletion.CASCADE,
                related_name='coupons',
                to=settings.AUTH_USER_MODEL,
                verbose_name='所属养殖户',
            ),
        ),
    ]
