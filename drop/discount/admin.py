from django.contrib import admin

from .models import ProductDiscount, Promocode, PromocodeUsage

@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
  filter_horizontal = ("products",)

@admin.register(Promocode)
class PromocodeAdmin(admin.ModelAdmin):
  pass

@admin.register(PromocodeUsage)
class PromocodeUsageAdmin(admin.ModelAdmin):
  pass
