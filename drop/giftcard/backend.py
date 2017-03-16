from django.conf import settings
from django.shortcuts import get_object_or_404

from drop.exceptions import PaymentError
from drop.payment.api import PaymentAPI
from drop.payment.backends.abstract import PaymentBackend
from drop.util.cart import get_or_create_cart
from lablackey.loader import load_class

from .models import Credit, Debit

import decimal

class GiftCard(PaymentBackend):
  name = "giftcard"
  def charge(self,order,request):
    credit = get_object_or_404(Credit,code=request.POST['code'])
    balance = credit.remaining
    total = decimal.Decimal(request.POST['total'])
    if total > balance:
      raise PaymentError('Your gift card balance is $%s, please select a value equal to or less than that.'%balance)
    cart_total = get_or_create_cart(request,save=True).total_price
    if total > cart_total:
      raise PaymentError("Please select an amount less than or equal to your cart total, $%s."%cart_total)
    debit = Debit.objects.create(
      user=order.user,
      credit=credit,
      order=order,
      amount=total,
    )
    t = "gc__%s"%debit.id
    d = "Gift Card Debit #%s-%s"%(debit.credit.code,debit.id)
    PaymentAPI().confirm_payment(order,total, t, 'giftcard',d)
  def refund(self,transaction_id):
    #! TODO
    raise NotImplementedError("Refunding gift cards has not yet been set up. Please pester chris@lablackey.com")
