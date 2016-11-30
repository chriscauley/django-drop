from django.contrib import admin

from models import GiftCardProduct, Credit, Debit

@admin.register(GiftCardProduct)
class GiftCardProductAdmin(admin.ModelAdmin):
  pass

class DebitInline(admin.TabularInline):
  model = Debit
  extra = 0

@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
  inlines = [DebitInline]
