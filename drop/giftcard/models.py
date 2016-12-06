from django.conf import settings
from django.db import models
from django.utils import timezone

from drop.models import Product, Order
from drop.util.fields import CurrencyField

from lablackey.decorators import cached_property
from lablackey.mail import send_template_email

import datetime, random, jsonfield

class GiftCardProduct(Product):
  has_quantity = False
  in_stock = 1e6
  extra_fields = ['recipient_name','recipient_email','delivery_date','amount']
  class Meta:
    app_label = "giftcard"
  def purchase(self,user,quantity):
    credit = Credit.objects.create(
      code=''.join([random.choice("0123456789ABCDEF") for i in range(16)]),
      purchased_by=user,
      amount=quantity,
      product=self,
      recipient_email=self.data['recipient_email']
    )
    if credit.delivery_date <= datetime.date.today():
      credit.send()

class Credit(models.Model):
  code = models.CharField(max_length=16)
  created = models.DateTimeField(auto_now_add=True)
  purchased_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="+")
  owner = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True)
  delivery_date = models.DateField(default=datetime.date.today)
  delivered = models.DateTimeField(null=True,blank=True)
  product = models.ForeignKey(GiftCardProduct)
  amount = CurrencyField()
  data = jsonfield.JSONField(default=dict,null=True,blank=True)
  @cached_property
  def remaining(self):
    return self.amount - sum(self.giftcardpurchase_set.all().values_list('amount',flat=True))
  __unicode__ = lambda self: self.code
  def send(self):
    if self.delivered:
      return
    to = [self.recipient_email or self.purchased_by.email]
    send_tempalte_email("email/send_giftcard",to,context={'credit': self})
    self.delivered  = timezone.now()
    self.save()

class Debit(models.Model):
  credit = models.ForeignKey(Credit)
  date_used = models.DateTimeField(auto_now_add=True)
  amount = CurrencyField()

  # cache the order, but if it gets deleted don't delete this!
  order = models.ForeignKey(Order,null=True,blank=True,on_delete=models.SET_NULL)
  __unicode__ = lambda self: "%s debited for %s"%(self.credit,self.amount)
