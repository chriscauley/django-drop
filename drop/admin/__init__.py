# flake8: noqa
from django.contrib import admin

from drop.models import Category, Product
from drop.admin import orderadmin

from lablackey.db.admin import NamedTreeModelAdmin

@admin.register(Category)
class CategoryAdmin(NamedTreeModelAdmin):
  list_filter = ("level",)
  list_display = ("__str__","featured")
  list_editable = ("featured",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display = ("__str__","order")
  list_editable = ("order",)
