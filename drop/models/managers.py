# -*- coding: utf-8 -*-
from django.core.mail import mail_admins
from django.db import models
from django.db.models.aggregates import Count
from polymorphic.manager import PolymorphicManager

from drop.order_signals import processing
from drop.util.compat.db import atomic


#==============================================================================
# Product
#==============================================================================

class ProductStatisticsManager(PolymorphicManager):
    """
    A Manager for all the non-object manipulation needs, mostly statistics and
    other "data-mining" toys.
    """

    def top_selling_products(self, quantity):
        """
        This method "mines" the previously passed orders, and gets a list of
        products (of a size equal to the quantity parameter), ordered by how
        many times they have been purchased.
        """
        # Importing here is fugly, but it saves us from circular imports...
        from drop.models.ordermodel import OrderItem
        # Get an aggregate of product references and their respective counts
        top_products_data = OrderItem.objects.values(
                'product').annotate(
                    product_count=Count('product')
                ).order_by('product_count'
            )[:quantity]

        # The top_products_data result should be in the form:
        # [{'product_reference': '<product_id>', 'product_count': <count>}, ..]

        top_products_list = []  # The actual list of products
        for values in top_products_data:
            prod = values.get('product')
            # We could eventually return the count easily here, if needed.
            top_products_list.append(prod)

        return top_products_list


class ProductManager(PolymorphicManager):
    """
    A more classic manager for Product filtering and manipulation.
    """
    def active(self):
        return self.filter(active=True)


#==============================================================================
# Order
#==============================================================================

class OrderManager(models.Manager):
    @atomic
    def get_or_create_from_cart(self, cart, request):
        """
        return a unique order for a given cart.

        Specifically, it creates an Order with corresponding OrderItems and
        eventually corresponding ExtraPriceFields

        This will only actually commit the transaction once the function exits
        to minimize useless database access.

        Emits the ``processing`` signal.
        """
        # must be imported here!
        from drop.models.ordermodel import (
            ExtraOrderItemPriceField,
            ExtraOrderPriceField,
            OrderItem,
        )
        from drop.models.cartmodel import CartItem

        try:
            order = self.model.objects.get(cart_pk=cart.pk)
        except self.model.DoesNotExist:
            order = self.model()
        except self.model.MultipleObjectsReturned:
            # just get rid of the rest
            order = self.model.objects.filter(cart_pk=cart.pk)[0]
            self.model.objects.exclude(pk=order.pk).filter(cart_pk=cart.pk).delete()

        # If the order and cart items to not match then they have most likely started a new cart
        # and the old order payment hasn't come through yet
        # dissociate the old cart and create a new order with the new cart
        if order.items.all():
            order_item_pks = sorted(order.items.all().values_list("product_id",flat=True))
            cart_item_pks = sorted(cart.items.all().values_list("product_id",flat=True))
            if cart_item_pks != order_item_pks:
                mail_admins("dissociating %s from %s"%(order.pk,cart.pk),
                            "This is a bit untested, go check in admin")
                order.cart_pk=None
                order.save()
                order = self.model()

        order.cart_pk = cart.pk
        order.user = cart.user
        order.status = self.model.PROCESSING  # Processing
        order.order_subtotal = cart.subtotal_price
        order.order_total = cart.total_price
        order.save()

        # Let's serialize all the extra price arguments in DB
        #! TODO This is not idempotent... may duplicate a field if there are subtle changes.
        for field in cart.extra_price_fields:
            ExtraOrderPriceField.objects.get_or_create(
                order=order,
                label=unicode(field[0]),
                value=field[1],
                data=field[2] if len(field) == 3 else None
            )

        # There, now move on to the order items.
        cart_items = CartItem.objects.filter(cart=cart)
        order_item_ids = []
        for item in cart_items:
            item.update(request)
            try:
                order_item = order.items.get(product=item.product)
            except OrderItem.DoesNotExist:
                order_item = OrderItem()
            order_item.order = order
            order_item.product_reference = item.product.get_product_reference()
            order_item.product_name = item.product.get_name()
            order_item.product = item.product
            order_item.unit_price = item.product.get_price()
            order_item.quantity = item.quantity
            order_item.line_total = item.line_total
            order_item.line_subtotal = item.line_subtotal
            order_item.extra = item.extra
            order_item.save()
            order_item_ids.append(order_item.id)
            # For each order item, we save the extra_price_fields to DB
            #! TODO This is not idempotent... may duplicate a field if there are subtle changes.
            for field in item.extra_price_fields:
                kwargs = dict(
                    order_item=order_item,
                    label = unicode(field[0]),
                    value = field[1]
                )
                if len(field) == 3:
                    kwargs['data'] = field[2]
                ExtraOrderItemPriceField.objects.get_or_create(**kwargs)

        # remove items that were removed from cart
        order.items.exclude(id__in=order_item_ids).delete()

        processing.send(self.model, order=order, cart=cart)
        return order
