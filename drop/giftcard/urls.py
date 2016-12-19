from django.conf.urls import url

import lablackey.views
import views

urlpatterns = [
  url(r'^redeem/$',lablackey.views.single_page_app,name="giftcard_redeem"),
  url(r'^user.json$',views.user_json),
  url(r'^redeem_ajax/$',views.redeem_ajax),
  url(r'^validate/$',views.validate)
]
