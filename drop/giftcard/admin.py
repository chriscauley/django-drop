from django.contrib import admin

from models import GiftCardProduct, Credit, Debit

@admin.register(GiftCardProduct)
class GiftCardProductAdmin(admin.ModelAdmin):
  pass

@admin.register(Debit)
class DebitAdmin(admin.ModelAdmin):
  raw_id_fields = ['order','user']

@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
  raw_id_fields = ['purchased_by','user','product']
