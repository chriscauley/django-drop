# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-07-16 20:44
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('drop', '0006_auto_20170211_2031'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='extra',
            field=jsonfield.fields.JSONField(blank=True, default=dict),
        ),
    ]
