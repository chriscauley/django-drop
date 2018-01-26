# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-08-09 20:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0006_auto_20170709_2014'),
    ]

    operations = [
        migrations.AddField(
            model_name='productdiscount',
            name='dollars',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='promocode',
            name='dollars',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='productdiscount',
            name='percentage',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='name',
            field=models.CharField(max_length=32, unique=True),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='percentage',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]