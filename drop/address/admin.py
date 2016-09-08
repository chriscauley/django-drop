#-*- coding: utf-8 -*-
from django.contrib import admin
from .models import Country, Address

#class ClientAdmin(ModelAdmin):
#    pass
#admin.site.register(Client, ClientAdmin)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'address', 'address2', 'zip_code', 'city', 'country',
        'user_shipping', 'user_billing')
    raw_id_fields = ('user_shipping', 'user_billing')


