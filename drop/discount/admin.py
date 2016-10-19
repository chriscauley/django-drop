from django.contrib import admin

from .models import ProductDiscount

@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
  filter_horizontal = ("products",)
