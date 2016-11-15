#-*- coding: utf-8 -*-
from django.contrib import admin
from .models import Address

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'address2', 'zip_code', 'city', 'user')
    raw_id_fields = ('user',)


