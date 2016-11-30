from django.conf import settings
from django.db import models

from drop.models import Product, Order
from drop.util.fields import CurrencyField

from lablackey.decorators import cached_property

class GiftCardProduct(Product):
  has_quantity = True
  in_stock = 1e6
  class Meta:
    app_label = "giftcard"
  def purchase(self,user,quantity):
    Credit.objects.create(
      code=''.join([random.choice("0123456789ABCDEF") for i in range(16)]),
      purchased_by=user,
      amount=quantity,
    )
  

class Credit(models.Model):
  code = models.CharField(max_length=16)
  created = models.DateTimeField(auto_now_add=True)
  purchased_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="+")
  owner = models.ForeignKey(settings.AUTH_USER_MODEL)
  recepiant_email = models.EmailField(null=True,blank=True)
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
