# -*- coding: utf-8 -*-
from django.conf import settings
from django.urls import include, re_path

from drop import views
from drop.discount import urls as discount_urls
from drop.views import checkout as checkout_views

urlpatterns = [
  re_path(r'^$',views.index,name='product_list'),
  re_path(r'^product/(\d+)/([0-9A-Za-z-_.//]+)/$', views.detail, name='product_detail'),
  re_path(r'^products.js',views.ajax.products_json,name='products_json'),
  re_path(r'^cart.js$',views.ajax.cart_json,name='cart_json'),
  re_path(r'^ajax/', include('drop.urls.ajax')),
  re_path(r'^orders/', include('drop.urls.order')),
  re_path(r'^thank_you/(\d+)/$', checkout_views.thank_you, name='checkout-thank_you'),
  #re_path(r'^checkout/', include('drop.urls.checkout')),
  #re_path(r'^cart/', include('drop.urls.cart')),
  re_path(r'^(stripe|giftcard)/payment/$',views.ajax.payment,name="drop_payment"),
  re_path('',include(discount_urls)),

  #! TODO: currently does nothing
  re_path(r'^category/(?P<category_id>\d+)/(?P<slug>[0-9A-Za-z-_.//]+)/$',views.detail,name='category_detail'),
]

for app in ['address','giftcard']:
  if 'drop.%s'%app in settings.INSTALLED_APPS:
    urlpatterns.append(re_path(r'^%s/'%app,include('drop.%s.urls'%app)))
