# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from drop.models.abstract import BaseCart


class Cart(BaseCart):
    class Meta(object):
        abstract = False
        app_label = 'drop'
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')
