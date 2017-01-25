from django.core.urlresolvers import reverse

from lablackey.tests import ClientTestCase

from drop.models import Product
import random, decimal

class DropTestCase(ClientTestCase):
  def add_to_cart(self,product,quantity=1,start_checkout=True):
    self.client.post(reverse('cart_edit'),{
      'id': product.id,
      'quantity': quantity
    })
    if start_checkout:
      return self.start_checkout()
  def start_checkout(self):
    _r = self.client.get(reverse('start_checkout'))
    return _r.json()['order_id']
  def new_product(self,name=None,unit_price=1):
    return self._new_object(Product,
                    name=name or "product%s"%random.random(),
                    unit_price=decimal.Decimal(unit_price)
                  )
