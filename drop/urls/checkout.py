from django.urls import re_path
from drop.util.decorators import cart_required

from drop.views import checkout as views
from drop.views.checkout import (
    CheckoutSelectionView,
    PaymentBackendRedirectView,
    ShippingBackendRedirectView,
    OrderConfirmView,
)

urlpatterns = [
  re_path(r'^$', cart_required(CheckoutSelectionView.as_view()),name='checkout_selection'),
  re_path(r'^ship/$', ShippingBackendRedirectView.as_view(),name='checkout_shipping'),
  re_path(r'^confirm/$', OrderConfirmView.as_view(),name='checkout_confirm'),
  re_path(r'^pay/$', PaymentBackendRedirectView.as_view(),name='checkout_payment'),
  re_path(r'^thank_you/(\d+)/$', views.thank_you, name='checkout-thank_you')
]
