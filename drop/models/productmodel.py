# -*- coding: utf-8 -*-
"""
This overrides the Product model with the class loaded from the
DROP_PRODUCT_MODEL setting if it exists.
"""
from django.conf import settings
from lablackey.loader import load_class


#==============================================================================
# Extensibility
#==============================================================================
PRODUCT_MODEL = getattr(settings, 'DROP_PRODUCT_MODEL',
    'drop.models.defaults.product.Product')
Product = load_class(PRODUCT_MODEL, 'DROP_PRODUCT_MODEL')
