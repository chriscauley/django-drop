# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-12-21 10:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('giftcard', '0003_auto_20161220_1841'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='giftcardproduct',
            managers=[
            ],
        ),
        migrations.RemoveField(
            model_name='credit',
            name='delivered',
        ),
        migrations.RemoveField(
            model_name='credit',
            name='delivery_date',
        ),
    ]
