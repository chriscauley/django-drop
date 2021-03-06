# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from drop.models.abstract import BaseOrder
from drop.models.managers import OrderManager


class Order(BaseOrder):
    objects = OrderManager()

    class Meta(object):
        abstract = False
        app_label = 'drop'
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ('-created',)
