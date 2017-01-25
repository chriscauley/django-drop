from drop.test_utils import DropTestCase

from drop.backends_pool import payment_backends
from drop.models import Order
from drop.payment.api import PaymentAPI

from decimal import Decimal
import random

def print_order(order_id):
  print "-------------\nOrder #%s"%order_id
  order = Order.objects.get(pk=order_id)
  print "total: %s"%order.order_total
  for i in order.items.all():
    print i,'  ',i.line_total
  for op in order.orderpayment_set.all():
    print "payment: %s"%op.amount

class PaymentModuleTestCase(DropTestCase):
  def setUp(self):
    self.product10 = self.new_product(unit_price=10)
    self.product2 = self.new_product(unit_price=2)
  def test_paypal_double_purchase(self):
    user = self.new_user("auser")
    self.login(user)
    # Add an item to cart
    order_id = self.add_to_cart(self.product10)
    order = Order.objects.get(pk=order_id)
    print_order(order_id)
    self.assertEqual(order.items.count(),1)
    self.assertEqual(order.order_total,10)

    # Add another one but we're using the above un-updated order for the payment
    order2_id = self.add_to_cart(self.product2)
    print_order(order2_id)
    PaymentAPI().confirm_payment(order,Decimal(10),"faketransaction%s"%random.random(),'paypal',"Faked paypal payment")
    order = Order.objects.get(pk=order_id)
