# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2016-11-30 11:36
from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import drop.util.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('drop', '0008_auto_20161111_2219'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Credit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=16)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('recepiant_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('amount', drop.util.fields.CurrencyField(decimal_places=2, default=Decimal('0.0'), max_digits=30)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Debit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_used', models.DateTimeField(auto_now_add=True)),
                ('amount', drop.util.fields.CurrencyField(decimal_places=2, default=Decimal('0.0'), max_digits=30)),
                ('credit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='giftcard.Credit')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='drop.Order')),
            ],
        ),
        migrations.CreateModel(
            name='GiftCardProduct',
            fields=[
                ('product_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='drop.Product')),
            ],
            bases=('drop.product',),
        ),
        migrations.AddField(
            model_name='credit',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='giftcard.GiftCardProduct'),
        ),
        migrations.AddField(
            model_name='credit',
            name='purchased_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]