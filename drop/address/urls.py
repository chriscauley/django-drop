from django.conf.urls import include, url

import views

urlpatterns = [
  url(r'^add/$',views.add),
  url(r'^select/$',views.select),
]
