# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drop', '0002_remove_product_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='baseproduct',
            name='product_ptr',
        ),
        migrations.DeleteModel(
            name='BaseProduct',
        ),
    ]
