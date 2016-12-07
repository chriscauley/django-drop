# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url

from drop import views

urlpatterns = [
  url(r'^$',views.product.index,name='product_list'),
  url(r'^product/(\d+)/([0-9A-Za-z-_.//]+)/$', views.product.detail, name='product_detail'),
  url(r'^products.js',views.ajax.products_json,name='products_json'),
  url(r'^cart.js$',views.ajax.cart_json,name='cart_json'),
  url(r'^ajax/', include('drop.urls.ajax')),
  url(r'^orders/', include('drop.urls.order')),
  url(r'^checkout/', include('drop.urls.checkout')),
  url(r'^cart/', include('drop.urls.cart')),
  url(r'^(stripe|giftcard)/payment/$',views.ajax.payment,name="drop_payment"),
]

for app in ['address','giftcard']:
  if 'drop.%s'%app in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'^%s/'%app,include('drop.%s.urls'%app)))
