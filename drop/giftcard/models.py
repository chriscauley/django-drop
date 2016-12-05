from django.conf import settings
from django.db import models

from drop.models import Product, Order
from drop.util.fields import CurrencyField

from lablackey.decorators import cached_property
from lablackey.mail import send_template_email

import datetime

class GiftCardProduct(Product):
  has_quantity = False
  in_stock = 1e6
  extra_fields = ['recipient_name','recipient_email','delivery_date','amount']
  class Meta:
    app_label = "giftcard"
  def purchase(self,user,quantity):
    Credit.objects.create(
      code=''.join([random.choice("0123456789ABCDEF") for i in range(16)]),
      purchased_by=user,
      amount=quantity,
    )
  @classmethod
  def send_payment_confirmation_email(cls,order,order_items):
    context = {'order': order, 'order_items': order_items}
    send_template_email('email/giftcard_confirmation',[order.user.email],context=context)

class Credit(models.Model):
  code = models.CharField(max_length=16)
  created = models.DateTimeField(auto_now_add=True)
  purchased_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="+")
  owner = models.ForeignKey(settings.AUTH_USER_MODEL)
  recepiant_email = models.EmailField(null=True,blank=True)
  delivery_date = models.DateField(default=datetime.date.today)
  product = models.ForeignKey(GiftCardProduct)
  amount = CurrencyField()
  @cached_property
  def remaining(self):
    return self.amount - sum(self.giftcardpurchase_set.all().values_list('amount',flat=True))
  __unicode__ = lambda self: self.code

class Debit(models.Model):
  credit = models.ForeignKey(Credit)
  date_used = models.DateTimeField(auto_now_add=True)
  amount = CurrencyField()

  # cache the order, but if it gets deleted don't delete this!
  order = models.ForeignKey(Order,null=True,blank=True,on_delete=models.SET_NULL)
  __unicode__ = lambda self: "%s debited for %s"%(self.credit,self.amount)
