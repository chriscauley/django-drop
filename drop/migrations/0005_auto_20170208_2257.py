# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-02-08 22:57
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drop', '0004_cart_extra'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='modified',
            new_name='updated'
        ),
    ]