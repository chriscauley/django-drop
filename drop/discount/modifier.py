from django.conf import settings

from drop.cart.cart_modifiers_base import BaseCartModifier
from lablackey.loader import load_class
from .models import ProductDiscount, Promocode

from decimal import Decimal, ROUND_DOWN
import six

class ProductDiscountCartModifier(BaseCartModifier):
  def get_extra_cart_item_price_field(self, cart_item, request):
    discounts = cart_item.product.productdiscount_set.all()
    if discounts:
      discount = discounts.order_by("-percentage")[0]
      amount = Decimal(int(-cart_item.product.unit_price*cart_item.quantity*discount.percentage))/100
      return [unicode(discount),amount]

class UserDiscountCartModifier(BaseCartModifier):
  def get_extra_cart_price_field(self,cart,request):
    f = getattr(settings,"DROP_USER_DISCOUNT_FUNCTION",None)
    if not (f and request.user.is_authenticated()):
      return

    if isinstance(f,six.string_types):
      f = load_class(f)
    return f(cart,request.user)
  def get_extra_cart_item_price_field(self,cart_item,request):
    f = getattr(settings,"DROP_USER_DISCOUNT_ITEM_FUNCTION",None)
    if not (f and request.user.is_authenticated()):
      return

    if isinstance(f,six.string_types):
      f = load_class(f)
    return f(cart_item,request.user)

class PromocodeCartModifier(BaseCartModifier):
  def get_extra_cart_item_price_field(self,cart_item,request):
    cart = cart_item.cart
    if cart.extra.get('promocode',None):
      try:
        promocode = Promocode.objects.get(pk=cart.extra['promocode']['id'])
      except Promocode.DoesNotExist:
        return
      if promocode.expired or not promocode.matches_product(cart_item.product):
        return
      amount = Decimal(-cart_item.quantity*promocode.dollars)
      if promocode.percentage:
        amount = Decimal(int(-cart_item.product.unit_price*cart_item.quantity*promocode.percentage))/100
      return (promocode.name,amount)
