from django.urls import re_path

from drop.discount import views

urlpatterns = [
  re_path('^promocode/redeem_ajax/$',views.redeem_ajax,name='promocode_redeem_ajax'),
]
