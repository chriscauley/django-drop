from django.urls import re_path

from drop.address import views

urlpatterns = [
  re_path(r'^add/$',views.add),
  re_path(r'^select/$',views.select),
]
