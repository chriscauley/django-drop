# -*- coding: utf-8 -*-
from django.conf.urls import include, url

from drop import views
from drop.views.product import ProductListView

urlpatterns = [
  url(r'^$',ProductListView.as_view(),name='product_list'),
  url(r'^product/(\d+)/([0-9A-Za-z-_.//]+)/$', views.product.detail, name='product_detail'),
  url(r'^products.js',views.ajax.products_json,name='products_json'),
  url(r'^cart.js$',views.ajax.cart_json,name='cart_json'),
  url(r'^ajax/', include('drop.urls.ajax')),
  url(r'^pay/', include('drop.payment.urls')),
  url(r'^ship/', include('drop.shipping.urls')),
  url(r'^orders/', include('drop.urls.order')),
  url(r'^checkout/', include('drop.urls.checkout')),
  url(r'^cart/', include('drop.urls.cart')),
  url(r'^stripe/payment/$',views.ajax.stripe_payment),
]
