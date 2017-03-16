# -*- coding: utf-8 -*-
"""
This overrides the various models with classes loaded from the corresponding
setting if it exists.
"""
from django.conf import settings
from lablackey.loader import load_class


#==============================================================================
# Extensibility
#==============================================================================
# Cart model
CART_MODEL = getattr(settings, 'DROP_CART_MODEL',
    'drop.models.defaults.cart.Cart')
Cart = load_class(CART_MODEL, 'DROP_CART_MODEL')

# Cart item model
CARTITEM_MODEL = getattr(settings, 'DROP_CARTITEM_MODEL',
    'drop.models.defaults.cartitem.CartItem')
CartItem = load_class(CARTITEM_MODEL, 'DROP_CARTITEM_MODEL')
