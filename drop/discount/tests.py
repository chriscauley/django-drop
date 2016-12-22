from django.core.urlresolvers import reverse

from drop.test_utils import DropTestCase
from drop.models import Order
from .models import ProductDiscount

class DiscountTestCase(DropTestCase):
  def setUp(self):
    self.product1 = self.new_product()
    self.product2 = self.new_product(unit_price=2)
    self.product10 = self.new_product(unit_price=10)
    self.product20 = self.new_product(unit_price=20)
  def test_user_discount(self):
    """ testapp.main.settings.drop says this guy should get a dollar off """
    user = self.new_user("give_me_one_dollar_off")
    order_id = self.add_to_cart(self.product1)
    self.assertEqual(Order.objects.get(id=order_id).order_total,self.product1.unit_price)
    self.login(user)
    self.client.get(reverse('start_checkout'))
    self.assertEqual(Order.objects.get(id=order_id).order_total,self.product1.unit_price-1)
  def test_product_discount(self):
    """ create two products, one with a discount, make sure they have the right price. """
    discount = ProductDiscount.objects.create(name="Test Discount",percentage=10)
    discount.products = [self.product10]
    discount.save()
    order_id = self.add_to_cart(self.product1)
    total = 1
    self.assertEqual(Order.objects.get(id=order_id).order_total,total)
    order_id = self.add_to_cart(self.product10)
    total += 9 # = 10 - 10%
    self.assertEqual(Order.objects.get(id=order_id).order_total,total)
    order_id = self.add_to_cart(self.product10,quantity=2)
    total += 9 # = 10 - 10%
    self.assertEqual(Order.objects.get(id=order_id).order_total,total)
    order_id = self.add_to_cart(self.product20,quantity=2)
    total += 2*20
    self.assertEqual(Order.objects.get(id=order_id).order_total,total)
