#-*- coding: utf-8 -*-
from django.conf import settings
from drop.util.loader import load_class
from collections import OrderedDict

def _load_backends_list(setting_name):
    out = OrderedDict()
    for s in getattr(settings, setting_name, []):
        o = load_class(s)()
        out[o.name] = o
    return out

payment_backends = _load_backends_list('DROP_PAYMENT_BACKENDS')
shippping_backends = _load_backends_list('DROP_SHIPPING_BACKENDS')
