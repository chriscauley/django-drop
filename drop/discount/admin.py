from django.conf import settings
from django.contrib import admin

from .models import ProductDiscount, Promocode, PromocodeUsage

@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
  filter_horizontal = ("products",)

@admin.register(Promocode)
class PromocodeAdmin(admin.ModelAdmin):
  readonly_fields = ("direct_link",)
  def direct_link(self,obj):
    url = "%s?p=%s"%(settings.SITE_URL,obj.code)
    return "<a href='%s'>%s</a><br/>%s"%(url,obj.name,url)
  direct_link.allow_tags = True

@admin.register(PromocodeUsage)
class PromocodeUsageAdmin(admin.ModelAdmin):
  list_display = ['__unicode__','created']
  readonly_fields = ['promocode','order','created']
