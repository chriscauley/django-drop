# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-01-30 16:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0003_auto_20170130_1220'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promocodeusage',
            name='user',
        ),
    ]
