from django.conf.urls import patterns, include, url
from example.mydrop.views import MyOrderConfirmView

from drop import urls as drop_urls
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),

    url(r'^checkout/confirm/$', MyOrderConfirmView.as_view(), name='checkout_shipping'),
    (r'^', include(drop_urls)), # <-- That's the important bit
)
