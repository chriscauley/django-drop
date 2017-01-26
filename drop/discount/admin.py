from django.contrib import admin

from .models import ProductDiscount, PromocodeDiscount

@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
  filter_horizontal = ("products",)

@admin.register(PromocodeDiscount)
class PromocodeDiscountAdmin(admin.ModelAdmin):
  pass
