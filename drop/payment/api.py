# -*- coding: utf-8 -*-

"""
This file defines the interfaces one should implement when either creating a
new payment module or willing to use modules with another drop system.
"""
from decimal import Decimal
from drop.models import Cart
from drop.models.ordermodel import OrderPayment
from drop.models.ordermodel import Order
from drop.drop_api import DropAPI
from drop.order_signals import completed
from django.core.urlresolvers import reverse

class PaymentAPI(DropAPI):
    """
    This object's purpose is to expose an API to the drop system.
    Ideally, drops (django DROP or others) should implement this API, so that
    payment plugins are interchangeable between systems.

    This implementation is the interface reference for django DROP

    Don't forget that since plenty of methods are common to both PaymentAPI
    and ShippingAPI(), they are defined in the DropAPI base class!
    """

    #==========================================================================
    # Payment-specific
    #==========================================================================

    def confirm_payment(self, order, amount, transaction_id, payment_method,
                        save=True):
        """
        Marks the specified amount for the given order as paid.
        This allows to hook in more complex behaviors (like saving a history
        of payments in a Payment model)
        The optional save argument allows backends to explicitly not save the
        order yet
        """
        OrderPayment.objects.create(
            order=order,
            # How much was paid with this particular transfer
            amount=Decimal(amount),
            transaction_id=transaction_id,
            payment_method=payment_method)
        
        if save and self.is_order_paid(order):
            # Set the order status:
            order.status = Order.COMPLETED
            order.save()

            # fire the purchase method for products to update inventory or whatever
            for item in order.items.all():
                item.product.purchase(item.quantity)
            # empty the related cart
            try:
                cart = Cart.objects.get(pk=order.cart_pk)
                cart.empty()
            except Cart.DoesNotExist:
                pass

            completed.send(sender=self, order=order)


    #==========================================================================
    # URLS
    #==========================================================================
    # Theses simply return URLs to make redirections easier.
    def get_finished_url(self):
        """
        A helper for backends, so that they can call this when their job
        is finished i.e. The payment has been processed from a user perspective
        This will redirect to the "Thanks for your order" page.
        
        To confirm the payment, call confirm_payment before this function. 
        For example, for PayPal IPN, the payment is confirmed upon receipt 
        of an Instant Payment Notification, and later this function is called 
        when the user is directed back from PayPal.
        """
        return reverse('thank_you_for_your_order')

    def get_cancel_url(self):
        """
        A helper for backends to let them redirect to a generic "order was
        cancelled" URL of their choosing.
        """
        return reverse('checkout_payment')
