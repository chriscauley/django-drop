from __future__ import unicode_literals

from django.db import models
from drop.models import Product, JsonMixin

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
