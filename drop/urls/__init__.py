# -*- coding: utf-8 -*-
from django.conf.urls import include, url

from shop.views import ShopTemplateView

urlpatterns = [
  url(r'^$', ShopTemplateView.as_view(template_name="shop/welcome.html"),name='shop_welcome'),
  url(r'^pay/', include('shop.payment.urls')),
  url(r'^ship/', include('shop.shipping.urls')),
  url(r'^orders/', include('shop.urls.order')),
  url(r'^checkout/', include('shop.urls.checkout')),
  url(r'^cart/', include('shop.urls.cart')),
  url(r'^products/', include('shop.urls.catalog')),
]
