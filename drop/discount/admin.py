from django.conf import settings
from django.contrib import admin

from .models import ProductDiscount, Promocode, PromocodeUsage

@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
  filter_horizontal = ("products",)

@admin.register(Promocode)
class PromocodeAdmin(admin.ModelAdmin):
  readonly_fields = ("direct_link",)
  filter_horizontal = ['product_types','products']
  def direct_link(self,obj):
    url = "%s?p=%s"%(settings.SITE_URL,obj.code)
    return "<a href='%s'>%s</a><br/>%s"%(url,obj.name,url)
  direct_link.allow_tags = True

@admin.register(PromocodeUsage)
class PromocodeUsageAdmin(admin.ModelAdmin):
  list_display = ['__unicode__','created','user','order_summary']
  readonly_fields = ['promocode','order','created']
  def user(self,obj):
    return obj.order.user
  def order_summary(self,obj):
    out = ""
    order = obj.order
    out += "<a href='%s'>Order #%s - $%s</a><br/>-----"%(order.get_admin_url(),order.id,order.order_total)
    for item in order.items.all():
      out += "<br/>%sx$%s %s"%(item.quantity,item.unit_price,item.product_name)
    return out
  order_summary.allow_tags = True
