from drop.backends_pool import payment_backends
from drop.models import Order
from drop.payment.api import PaymentAPI
from drop.test_utils import DropTestCase, print_order

from decimal import Decimal
import random

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
    #print_order(order_id)
    self.assertEqual(order.items.count(),1)
    self.assertEqual(order.order_total,10)

    # Add another one but we're using the above un-updated order for the payment
    order2_id = self.add_to_cart(self.product2)
    PaymentAPI().confirm_payment(order,Decimal(10),"faketransaction%s"%random.random(),'paypal',"Faked paypal payment")
    #print_order(order_id) #passing in id causes it to re look up order
    #print_order(order2_id)
