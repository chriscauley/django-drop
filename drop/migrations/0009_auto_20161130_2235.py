# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-11-30 22:35
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('drop', '0008_auto_20161111_2219'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='extra',
            field=jsonfield.fields.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='extra',
            field=jsonfield.fields.JSONField(default=dict),
        ),
    ]
