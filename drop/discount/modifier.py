from drop.cart.cart_modifiers_base import BaseCartModifier
from .models import ProductDiscount

from decimal import Decimal, ROUND_DOWN

class ProductDiscountCartModifier(BaseCartModifier):
  def get_extra_cart_item_price_field(self, cart_item, request):
    discounts = cart_item.product.productdiscount_set.all()
    if discounts:
      discount = discounts.order_by("-percentage")[0]
      amount = Decimal(int(-cart_item.product.unit_price*cart_item.quantity*discount.percentage))/100
      return [unicode(discount),amount]
