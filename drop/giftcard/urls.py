from django.urls import re_path

import lablackey.views
from drop.giftcard import views

urlpatterns = [
  re_path(r'^redeem/$',lablackey.views.single_page_app,name="giftcard_redeem"),
  re_path(r'^user.json$',views.user_json),
  re_path(r'^redeem_ajax/$',views.redeem_ajax,name="giftcard_redeem_ajax"),
  re_path(r'^validate/$',views.validate),
  re_path(r'^([\d\w]+).png$',views.image,name="giftcard_image"),
  re_path(r'^([\d\w]+).jpg$',views.image), #just in case
]
