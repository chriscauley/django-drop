from django.conf import settings

from drop.cart.cart_modifiers_base import BaseCartModifier
from drop.util.loader import load_class
from .models import ProductDiscount

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
