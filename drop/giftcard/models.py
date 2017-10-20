from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone

from drop.models import Product, Order
from drop.util.fields import CurrencyField

from lablackey.db.models import JsonMixin
from lablackey.decorators import cached_property
from lablackey.mail import send_template_email
from media.models import PhotosMixin

import datetime, random, jsonfield

class GiftCardProduct(Product,PhotosMixin):
  has_quantity = False
  in_stock = 1e6
  extra_fields = ['to','from','amount']
  class Meta:
    app_label = "giftcard"
  def purchase_message(self):
    return "Information on how to print and redeem your gift card will be sent to your email address. Be sure to check your spam folder if you do not see this email in the next 10 minutes."
  def purchase(self,order_item):
    user = order_item.order.user
    quantity = order_item.quantity
    credit = Credit.make_random(
      quantity,
      purchased_by=user,
      product=self,
      extra=order_item.extra,
    )
    credit.send()
    order_item.extra['purchased_model'] = "giftcard.Credit"
    order_item.extra['purchased_pk'] = credit.pk
    order_item.save()

class Credit(models.Model,JsonMixin):
  def __init__(self,*args,**kwargs):
    # necessary for refund api
    #! TODO after test coverage is complete lets rename Credit.amount to credit.quantity
    super(Credit,self).__init__(*args,**kwargs)
    self.quantity = int(self.amount)

  code = models.CharField(max_length=16,unique=True)
  created = models.DateTimeField(auto_now_add=True)
  purchased_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="+",null=True,blank=True)
  user = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True)
  product = models.ForeignKey(GiftCardProduct)
  amount = CurrencyField()
  extra = jsonfield.JSONField(default=dict,null=True,blank=True)
  json_fields = ['created','remaining','code','extra']

  def get_image_url(self):
    return reverse("giftcard_image",args=[self.code])

  def get_absolute_url(self):
    url = getattr(settings,"DROP_GIFTCARD_LANDING",None) or reverse("giftcard_redeem")
    return "%s?giftcode=%s"%(url,self.code)
  @cached_property
  def remaining(self):
    return self.amount - sum(self.debit_set.all().values_list('amount',flat=True))
  __unicode__ = lambda self: self.code
  def send(self):
    to = [self.purchased_by.email]
    context = {'credit': self, 'user_display': self.purchased_by.get_full_name() or self.purchased_by.username}
    attrs = ['DROP_GIFTCARD_IMG','DROP_GIFTCARD_FONT']
    context['GIFTCARD_IMAGE'] = all([getattr(settings,a,None) for a in attrs])
    send_template_email("email/send_giftcard",to,context=context,bcc=['cauley.chris@gmail.com'])
    self.save()

  @classmethod
  def make_random(clss,amount,**kwargs):
    count = 1
    if not 'product' in kwargs:
      kwargs['product'] = GiftCardProduct.objects.all()[0] # typically a site will only have one giftcard product
    while count:
      code = ''.join([random.choice("0123456789ABCDEF") for i in range(8)])
      count = clss.objects.filter(code=code).count()
    return clss.objects.create(
      amount=amount,
      code=code,
      **kwargs
    )

class Debit(models.Model,JsonMixin):
  user = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True)
  credit = models.ForeignKey(Credit)
  order = models.ForeignKey(Order)
  created = models.DateTimeField(auto_now_add=True)
  amount = CurrencyField()
  json_fields = ['created']

  # cache the order, but if it gets deleted don't delete this!
  order = models.ForeignKey(Order,null=True,blank=True,on_delete=models.SET_NULL)
  __unicode__ = lambda self: "%s debited for %s"%(self.credit,self.amount)
