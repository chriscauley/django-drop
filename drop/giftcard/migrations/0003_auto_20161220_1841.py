# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-20 18:41
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('giftcard', '0002_debit_credit'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='giftcardproduct',
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('base_objects', django.db.models.manager.Manager()),
            ],
        ),
    ]