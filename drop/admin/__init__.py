# flake8: noqa
from django.contrib import admin

from drop.models import Category, Product
import orderadmin

from lablackey.db.admin import NamedTreeModelAdmin

@admin.register(Category)
class CategoryAdmin(NamedTreeModelAdmin):
  list_filter = ("level",)
  list_display = ("__unicode__","featured")
  list_editable = ("featured",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display = ("__unicode__","order")
  list_editable = ("order",)
