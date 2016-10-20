# flake8: noqa
from django.contrib import admin

from drop.models import Category
import orderadmin

from lablackey.db.admin import NamedTreeModelAdmin

@admin.register(Category)
class CategoryAdmin(NamedTreeModelAdmin):
  pass
