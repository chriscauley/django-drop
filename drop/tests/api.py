from drop.models.ordermodel import OrderExtraInfo, Order
from django.test.testcases import TestCase
from django.contrib.auth.models import User
from drop.tests.util import Mock
from drop.drop_api import DropAPI
from decimal import Decimal


class DropApiTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="test",
            email="test@example.com")

        self.request = Mock()
        setattr(self.request, 'user', None)

        self.order = Order()
        self.order.order_subtotal = Decimal('10.95')
        self.order.order_total = Decimal('10.95')
        self.order.shipping_cost = Decimal('0')

        self.order.shipping_address_text = 'shipping address example'
        self.order.billing_address_text = 'billing address example'

        self.order.save()

    def test_add_extra_info(self):
        api = DropAPI()
        api.add_extra_info(self.order, 'test')
        # Assert that an ExtraOrderInfo item was created
        oei = OrderExtraInfo.objects.get(order=self.order)
        self.assertEqual(oei.text, 'test')

    def test_is_order_paid(self):
        api = DropAPI()
        # Ensure deprecated method still works
        res = api.is_order_paid(self.order)
        self.assertEqual(res, False)

    def test_is_order_complete(self):
        api = DropAPI()
        res = api.is_order_completed(self.order)
        self.assertEqual(res, False)

    def test_get_order_total(self):
        api = DropAPI()
        res = api.get_order_total(self.order)
        self.assertEqual(res, Decimal('10.95'))

    def test_get_order_subtotal(self):
        api = DropAPI()
        res = api.get_order_subtotal(self.order)
        self.assertEqual(res, Decimal('10.95'))

    def test_get_order_short_name(self):
        api = DropAPI()
        res = api.get_order_short_name(self.order)
        self.assertEqual(res, '1-10.95')

    def test_get_order_unique_id(self):
        api = DropAPI()
        res = api.get_order_unique_id(self.order)
        self.assertEqual(res, 1)

    def test_get_order_for_id(self):
        api = DropAPI()
        res = api.get_order_for_id(1)
        self.assertEqual(res, self.order)
