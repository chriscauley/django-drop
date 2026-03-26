from django.urls import re_path
from drop.views.order import OrderListView, OrderDetailView

urlpatterns = [
  re_path(r'^$',OrderListView.as_view(),name='order_list'),
  re_path(r'^(?P<pk>\d+)/$',OrderDetailView.as_view(),name='order_detail'),
]

