from django.urls import include, re_path
from example.mydrop.views import MyOrderConfirmView

from drop import urls as drop_urls
from django.contrib import admin

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),

    re_path(r'^checkout/confirm/$', MyOrderConfirmView.as_view(), name='checkout_shipping'),
    re_path(r'^', include(drop_urls)), # <-- That's the important bit
]
