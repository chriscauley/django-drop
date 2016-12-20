from django.core.urlresolvers import reverse

from drop.test_utils import DropTestCase
from drop.models import Order

class DiscountTestCase(DropTestCase):
  def setUp(self):
    self.product1 = self.new_product()
    self.product2 = self.new_product(unit_price=2)
  def test_user_discount(self):
    """ testapp.main.settings.drop says this guy should get a dollar off """
    user = self.new_user("give_me_one_dollar_off")
    order_id = self.add_to_cart(self.product1)
    self.assertEqual(Order.objects.get(id=order_id).order_total,self.product1.unit_price)
    self.login(user)
    self.client.get(reverse('start_checkout'))
    self.assertEqual(Order.objects.get(id=order_id).order_total,self.product1.unit_price-1)
