from django.conf import settings
from django.db import models
from drop.models import Product, Order
from django.utils import timezone

from lablackey.db.models import JsonMixin

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

class Promocode(models.Model,JsonMixin):
  name = models.CharField(max_length=32,blank=True)
  code = models.SlugField(max_length=32,unique=True)
  percentage = models.IntegerField(default=0)
  start_date = models.DateField(default=timezone.now,help_text="First date promocode becomes active.")
  end_date = models.DateField(null=True,blank=True,help_text="Optional final day this promocode can be used")
  __unicode__ = lambda self: self.name
  json_fields = ['name','percentage','code']
  _lct = lambda: { 'model__in': [s.__name__.lower() for s in Product.__subclasses__()] }
  def _lct():
    return { 'model__in': [s.__name__.lower() for s in Product.__subclasses__()] }
  product_types = models.ManyToManyField("contenttypes.ContentType",limit_choices_to=_lct)
  @property
  def expired(self):
    today = timezone.now().date()
    return self.start_date > today or (self.end_date and self.end_date < today)
  def matches_product(self,product):
    for pt in self.product_types.all():
      if isinstance(product,pt.model_class()):
        return True

class PromocodeUsage(models.Model):
  promocode = models.ForeignKey(Promocode)
  order = models.ForeignKey(Order)
  created = models.DateTimeField(auto_now_add=True)
  __unicode__ = lambda self: "%s used on %s"%(self.promocode,self.order)
  class Meta:
    ordering = ("-created",)
