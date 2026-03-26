from django.urls import re_path
from drop.views import ajax as ajax_views

urlpatterns = [
  re_path(r'^$',ajax_views.index,name='product_list'),
  re_path(r'^start_checkout/$',ajax_views.start_checkout,name='start_checkout'),
  re_path(r'^edit/$',ajax_views.cart_edit,name='cart_edit'),
  
  re_path(r'^receipts/$',ajax_views.receipts,name='receipts'),
  re_path(r'^admin/$',ajax_views.admin_page,name='admin_page'),
  re_path(r'^admin/add/$',ajax_views.admin_add,name='admin_add'),
  re_path(r'^admin/products.json',ajax_views.admin_products_json,name='admin_products_json'),
]
