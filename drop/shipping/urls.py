#-*- coding: utf-8 -*-
"""
Loop over shipping backends defined in settings.DROP_SHIPPING_BACKENDS and add
their URLs to the shipping namespace. eg:
http://www.example.com/drop/ship/dhl
http://www.example.com/drop/ship/fedex
...
"""
from django.urls import include, re_path
from drop.backends_pool import backends_pool


urlpatterns = [
    re_path("^%s/" % backend.url_namespace, include(backend.get_urls()))
    for backend in backends_pool.get_shipping_backends_list()
]
