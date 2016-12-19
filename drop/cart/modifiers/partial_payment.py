#-*- coding: utf-8 -*-
from decimal import Decimal
from drop.cart.cart_modifiers_base import BaseCartModifier
from drop.models import Order

class PartialPaymentModifier(BaseCartModifier):
    def process_cart(self, cart, request):
        if cart.pk and Order.objects.filter(cart_pk=cart.pk):
            order = Order.objects.filter(cart_pk=cart.pk)[0]
            for orderpayment in order.orderpayment_set.all():
                cart.current_total = cart.current_total - orderpayment.amount
                cart.extra_price_fields.append((orderpayment.description,-orderpayment.amount))
        return cart
