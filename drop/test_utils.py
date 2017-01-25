from django.core.urlresolvers import reverse

from lablackey.tests import ClientTestCase

from drop.models import Product, Order
import random, decimal

def print_order(order):
  if type(order) == int:
    order = Order.objects.get(pk=order)
  print "\n-------------\nOrder#%s Cart#%s"%(order.id,order.cart_pk)
  print "total: %s"%order.order_total
  if order.is_paid():
    print "PAID!"
  for i in order.items.all():
    print i,'  ',i.line_total
  for op in order.orderpayment_set.all():
    print "payment: %s"%op.amount

class DropTestCase(ClientTestCase):
  def add_to_cart(self,product,quantity=1,start_checkout=True,extra={}):
    extra.update({
      'id': product.id,
      'quantity': quantity
    })
    self.client.post(reverse('cart_edit'),extra)
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
