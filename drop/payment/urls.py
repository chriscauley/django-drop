#-*- coding: utf-8 -*-
"""
Loop over payment backends defined in settings.DROP_PAYMENT_BACKENDS and add
their URLs to the payment namespace. eg:
http://www.example.com/drop/pay/paypal
http://www.example.com/drop/pay/pay-on-delivery
...
"""
from django.conf.urls import include
from drop.backends_pool import backends_pool


urlpatterns = [
  url('^%s/'%backend.url_namespace, include(backend.get_urls()))
  for backend in backends_pool.get_payment_backends_list()
]
