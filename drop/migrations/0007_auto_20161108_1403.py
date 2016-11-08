# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drop', '0006_product_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderpayment',
            name='refunded',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(default=10, verbose_name='Status', choices=[(10, 'Processing'), (20, 'Confirming'), (30, 'Confirmed'), (40, 'Completed'), (50, 'Shipped')]),
        ),
    ]
