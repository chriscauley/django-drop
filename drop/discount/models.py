from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from drop.models import Product

from lablackey.unrest import JsonMixin

class ProductDiscount(models.Model,JsonMixin):
  """
  Line item discounts that are automatically applied. E.g. an item on a clearance rack.
  Can be used as many times as desired in a given cart.
  """
  name = models.CharField(max_length=32,unique=True)
  percentage = models.IntegerField(default=0)
  products = models.ManyToManyField(Product,limit_choices_to={'active': True})
  product_ids = property(lambda self: list(self.products.filter(active=True).values_list("id",flat=True)))
  __unicode__ = lambda self: self.name
  json_fields = ['name','percentage','product_ids']

class PromocodeDiscount(models.Model,JsonMixin):
  name = models.CharField(max_length=32,blank=True)
  code = models.SlugField(max_length=32,unique=True)
  percentage = models.IntegerField(default=0)
  start_date = models.DateField(default=timezone.now,help_text="First date promocode becomes active.")
  end_date = models.DateField(null=True,blank=True,help_text="Optional final day this promocode can be used")
  __unicode__ = lambda self: self.name
  json_fields = ['name','percentage','code']
  product_types = models.ManyToManyField("contenttypes.ContentType")
