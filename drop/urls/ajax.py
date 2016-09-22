from django.conf.urls import url, include
from drop.views import ajax as ajax_views

urlpatterns = [
  url(r'^$',ajax_views.index,name='product_list'),
  url(r'^start_checkout/$',ajax_views.start_checkout,name='start_checkout'),
  url(r'^edit/$',ajax_views.cart_edit,name='cart_edit'),
  
  url(r'^receipts/$',ajax_views.receipts,name='receipts'),
  url(r'^admin/$',ajax_views.admin_page,name='admin_page'),
  url(r'^admin/add/$',ajax_views.admin_add,name='admin_add'),
  url(r'^admin/products.json',ajax_views.admin_products_json,name='admin_products_json'),
]
