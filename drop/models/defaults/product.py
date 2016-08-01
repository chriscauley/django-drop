# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from drop.models_bases import BaseProduct
from drop.models_bases.managers import (
    ProductManager,
    ProductStatisticsManager,
)


class Product(BaseProduct):
    objects = ProductManager()
    statistics = ProductStatisticsManager()

    class Meta(object):
        abstract = False
        app_label = 'drop'
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
