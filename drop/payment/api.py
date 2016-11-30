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
from drop.order_signals import paid, refunded
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse

from lablackey.mail import send_template_email

def send_message(request,message,status=messages.SUCCESS):
    if request and message:
        messages.add_message(request,status,message)

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

    def send_payment_confirmation_email(self,order):
        """
        Send a payment confirmation email. Certain products may need to send a confirmation seperately.
        Maybe eventually there will need to be a settings.DROP_MAIL_CONFIRMATION_NO_MATTER_WHAT option?
        """
        order_items = [i for i in order.items.all()]
        for cls in set([i.product.__class__ for i in order_items]):
            if not hasattr(cls,"send_payment_confirmation_email"):
                continue
            cls_items = [i for i in order_items if isinstance(i.product,cls)]
            cls.send_payment_confirmation_email(order,cls_items)
            order_items = [i for i in order_items if not isinstance(i.product,cls)]
        if not order_items:
            return
        template = getattr(settings,"DROP_PAYMENT_CONFIRMATION_EMAIL_TEMPLATE","email/payment_confirmation")
        from_email = getattr(settings,"DROP_SHOPKEEPER_EMAIL",settings.DEFAULT_FROM_EMAIL)
        send_template_email(template,[order.user.email],from_email=from_email,
                            context={'order': order,'items': order_items})

    def confirm_payment(self, order, amount, transaction_id, payment_method,
                        save=True):
        """
        Marks the specified amount for the given order as paid.
        This allows to hook in more complex behaviors (like saving a history
        of payments in a Payment model)
        The optional save argument allows backends to explicitly not save the
        order yet
        """
        #! TODO this bit should probably be in the "if save..." block below. Check rest of code base first
        OrderPayment.objects.get_or_create(
            order=order,
            amount=Decimal(amount),
            transaction_id=transaction_id,
            payment_method=payment_method)

        if save and self.is_order_paid(order):
            if order.status < Order.PAID:
                # first time completing order. fire the purchase method for products to update inventory or whatever
                for item in order.items.all():
                    item.product.purchase(order.user,item.quantity)
                self.send_payment_confirmation_email(order)
            # Set the order status:
            order.status = Order.PAID
            order.save()

            # empty the related cart
            try:
                cart = Cart.objects.get(pk=order.cart_pk)
                cart.empty()
            except Cart.DoesNotExist:
                pass

            paid.send(sender=self, order=order)

    def refund_order(self,order,request=None):
        if not order.status in [Order.PAID,Order.SHIPPED]:
            send_message(request,"Cannot refund this order because it was never paid.",messages.ERROR)
            return

        for item in order.items.all():
            message = item.product.refund(order.user,item.quantity)
            send_message(request,message)
        order.status = Order.REFUNDED
        order.save()

        for payment in order.orderpayment_set.filter(refunded=False):
            backend = payment_backends.get(payment.payment_method.lower())
            if backend:
                refund_id = backend.refund(payment.transaciton_id)
                order.orderpayment_set.create(
                    amount=-payment.amount,
                    transaction_id=refund_id,
                    payment_method=order.payment_method
                )
                send_message(request,"%s refunded via %s"%(payment.amount,backend.name))
            else: # catch all
                m = "%s was marked as refunded, but no refund could be issued for this payment method."%order
                send_message(request,m,messages.WARNING)
            payment.refunded = True
            payment.save()
        refunded.send(sender=self, order=order)

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
