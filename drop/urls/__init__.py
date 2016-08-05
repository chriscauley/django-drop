# -*- coding: utf-8 -*-
from django.conf.urls import include, url

from drop.views import DropTemplateView

urlpatterns = [
  url(r'^$', DropTemplateView.as_view(template_name="drop/welcome.html"),name='drop_welcome'),
  url(r'^products.js','drop.views.ajax.products_json'),
  url(r'^ajax/', include('drop.urls.ajax')),
  url(r'^pay/', include('drop.payment.urls')),
  url(r'^ship/', include('drop.shipping.urls')),
  url(r'^orders/', include('drop.urls.order')),
  url(r'^checkout/', include('drop.urls.checkout')),
  url(r'^cart/', include('drop.urls.cart')),
  url(r'^products/', include('drop.urls.catalog')),
]
