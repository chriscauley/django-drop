from django.contrib import admin
from drop.models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  pass
