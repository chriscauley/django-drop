from django.contrib import admin

from models import GiftCardProduct, Credit, Debit
from media.admin import TaggedPhotoAdmin

@admin.register(GiftCardProduct)
class GiftCardProductAdmin(TaggedPhotoAdmin):
  pass

@admin.register(Debit)
class DebitAdmin(admin.ModelAdmin):
  raw_id_fields = ['order','user']

class DebitInline(admin.TabularInline):
  extra = 0
  model = Debit

@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
  raw_id_fields = ['purchased_by','user','product']
  list_display = ['__unicode__','purchased_by','user','remaining']
  inlines = [DebitInline]
