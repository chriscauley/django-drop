from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import modify_settings, override_settings
from django.utils import timezone

from drop.test_utils import DropTestCase, print_order
from drop.models import Order, Cart
from .models import ProductDiscount, Promocode

import decimal, datetime

class PromocodeTestCase(DropTestCase):
  def test_promocode(self):
    """ test that the basic promocode works. """
    self.product1 = self.new_product()
    self.product2 = self.new_product(unit_price=2)
    promocode = Promocode.objects.create(
      name="Test Promocode",
      code="promocode",
      percentage=11
    )
    user = self.new_user()
    self.login(user)
    response = self.client.get(reverse("promocode_redeem_ajax")+"?code=promocode")
    response_code = response.json()['cart']['extra']['promocode']
    self.assertEqual(sorted(response_code.items()),sorted(promocode.as_json.items()))
    self.add_to_cart(self.product1,quantity=3)
    order_id = self.add_to_cart(self.product2)

    # promocode does not yet have any product_types so it doesn't apply to these products
    total = 3 + 2
    self.assertEqual(Order.objects.get(id=order_id).order_total,total)

    # apply promocode and make sure the order total changes
    promocode.product_types.add(ContentType.objects.get_for_model(self.product1))
    promocode.save()
    order_id = self.start_checkout()
    total = decimal.Decimal(total)
    total = total - (total*11/100)
    self.assertEqual(Order.objects.get(id=order_id).order_total,total)

    #! TODO test and make sure PromocodeUsage object is created after checkout

  def test_promocode_dates(self):
    # Make sure that a promocode that expired yesterday is expired
    promocode = Promocode.objects.create(
      name="Test Promocode",
      code="promocode",
      percentage=11,
      end_date=timezone.now().date()-datetime.timedelta(1)
    )
    response = self.client.get(reverse("promocode_redeem_ajax")+"?code=promocode")
    self.assertTrue("This promocode expired on " in response.json()['error'])
    # Make sure that a promocode that hasn't started gives the right error message
    promocode = Promocode.objects.create(
      name="Test Promocode 2",
      code="promocode2",
      percentage=22,
      start_date=timezone.now().date()+datetime.timedelta(1)
    )
    response = self.client.get(reverse("promocode_redeem_ajax")+"?code=promocode2")
    self.assertTrue('Promocode "promocode2" not valid until' in response.json()['error'])

def user_discount(cart,user):
  if user.username == "give_me_one_dollar_off":
    return ("Dollar off for being a pal",-1)

new_settings = dict(
  DROP_USER_DISCOUNT_FUNCTION = user_discount,
)

@override_settings(**new_settings)
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
    """ create two products, one with a discount, make sure they have the right price in cart. """
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
