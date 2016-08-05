from django.conf.urls import patterns, url
from drop.views.product import (ProductListView, ProductDetailView)


urlpatterns = [
  url(r'^$',ProductListView.as_view(),name='product_list'),
  url(r'^(?P<pk>\d+)/([0-9A-Za-z-_.//]+)/$', ProductDetailView.as_view(), name='product_detail'),
]
