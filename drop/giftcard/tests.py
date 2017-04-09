from django.core.urlresolvers import reverse

from drop.giftcard.models import GiftCardProduct, Credit
from drop.models import Order, Product
from drop.payment.api import PaymentAPI
from drop.test_utils import DropTestCase, print_order

from decimal import Decimal

class GiftCardTestCase(DropTestCase):
  def test_giftcard_purchase(self):
    gcp = GiftCardProduct.objects.create(name="gift card",unit_price=1,active=True)
    product40 = self.new_product(unit_price=40)
    product20 = self.new_product(unit_price=20)
    user1 = self.new_user()

    # user1 buys a giftcard
    self.login(user1)
    order_id = self.add_to_cart(gcp,50,extra={'to': 'jon','from': 'jan'})
    items = user1.cart.items.all()
    self.assertEqual(items.count(),1)
    self.assertEqual(items[0].extra['to'],'jon')
    self.assertEqual(items[0].extra['from'],'jan')
    order = Order.objects.get(id=order_id)
    #print_order(order)
    PaymentAPI().confirm_payment(order,order.order_total,"fake transaction","fake backend","fake description")
    credit = Credit.objects.get(purchased_by=user1)

    # user2 redeems giftcard
    user2 = self.new_user()
    self.login(user2)
    giftcard = self.client.post(reverse("giftcard_redeem_ajax"),{'code':credit.code}).json()['giftcard']
    self.assertEqual(giftcard['remaining'],'50.00')

    # user2 buys an entire cart using a giftcard
    order2_id = self.add_to_cart(product40)
    payment_url = reverse("drop_payment",args=["giftcard"])
    response = self.client.post(payment_url,{'code': credit.code,'total': 40})
    self.assertTrue(response.json()['next'].startswith('/thank_you/%s/?token='%order2_id))
    order2 = Order.objects.get(pk=order2_id)
    #print_order(order2)
    self.assertTrue(order2.is_paid())

    # gift card now says less money
    giftcard = self.client.post(reverse("giftcard_redeem_ajax"),{'code':credit.code}).json()['giftcard']
    self.assertEqual(giftcard['remaining'],'10.00')

    # user2 partially pays for a cart using a giftcrd
    order3 = Order.objects.get(pk=self.add_to_cart(product20))
    #print_order(order3)

    # Two partial payments work and take order cost down to $10
    response1 = self.client.post(payment_url,{'code': credit.code,'total': 5})
    response2 = self.client.post(payment_url,{'code': credit.code,'total': 5})
    self.assertEqual(len(response2.json()['extra_price_fields']),2)
    order3 = Order.objects.get(pk=order3.id)
    self.assertEqual(order3.amount_paid,Decimal(10))

    # Third fails because balance on gift card is zero
    response3 = self.client.post(payment_url,{'code': credit.code,'total': 5})
    self.assertTrue('Your gift card balance is $0.00' in response3.json()['error'])

    # user2 fully pays with another payment method
    PaymentAPI().confirm_payment(order3,10,"fake transaction","fake backend","fake description")
    self.assertTrue(Order.objects.get(pk=order3.id).is_paid())
