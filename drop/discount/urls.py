from django.conf.urls import url

from drop.discount import views

urlpatterns = [
  url('^promocode/redeem_ajax/$',views.redeem_ajax,name='promocode_redeem_ajax'),
]
