from django.conf.urls import url
from shop.util.decorators import cart_required

from shop.views.checkout import (
    CheckoutSelectionView,
    PaymentBackendRedirectView,
    ShippingBackendRedirectView,
    OrderConfirmView,
    ThankYouView,
)

urlpatterns = [
  url(r'^$', cart_required(CheckoutSelectionView.as_view()),name='checkout_selection'),
  url(r'^ship/$', ShippingBackendRedirectView.as_view(),name='checkout_shipping'),
  url(r'^confirm/$', OrderConfirmView.as_view(),name='checkout_confirm'),
  url(r'^pay/$', PaymentBackendRedirectView.as_view(),name='checkout_payment'),
  url(r'^thank_you/$', ThankYouView.as_view(), name='thank_you_for_your_order')
]
