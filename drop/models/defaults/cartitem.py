# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from drop.models_bases import BaseCartItem


class CartItem(BaseCartItem):
    class Meta(object):
        abstract = False
        app_label = 'drop'
        verbose_name = _('Cart item')
        verbose_name_plural = _('Cart items')
