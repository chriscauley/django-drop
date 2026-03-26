from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

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
    return format_html("<a href='{}'>{}</a><br/>{}", url, obj.name, url)

@admin.register(PromocodeUsage)
class PromocodeUsageAdmin(admin.ModelAdmin):
  list_display = ['__str__','created','user','order_summary']
  readonly_fields = ['promocode','order','created']
  def user(self,obj):
    return obj.order.user
  def order_summary(self,obj):
    out = ""
    order = obj.order
    out += format_html("<a href='{}'>Order #{} - ${}</a><br/>-----", order.get_admin_url(), order.id, order.order_total)
    for item in order.items.all():
      out += format_html("<br/>{}x${} {}", item.quantity, item.unit_price, item.product_name)
    return format_html(out)
