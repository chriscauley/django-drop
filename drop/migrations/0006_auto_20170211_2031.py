# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-02-11 20:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drop', '0005_auto_20170208_2257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
