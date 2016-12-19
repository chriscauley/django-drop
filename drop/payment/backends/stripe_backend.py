from django.conf import settings

from drop.util.loader import load_class

from djstripe.models import Customer, StripeCard
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

from drop.exceptions import PaymentError
from .abstract import PaymentBackend

class Stripe(PaymentBackend):
  name = "stripe"
  def charge(self,order,request):
    kwargs = {
      'amount': int(float(request.POST['total'])*100), # Amount in cents
      'source': request.POST['token'],
      'currency': "usd",
      'description': "Payment for order #%s"%order.id,
      'metadata': {"order_id": order.id},
    }
    customer = None
    card = None
    user = order.user
    if not user and request.POST.get('email',None):
      f = load_class(getattr(settings, 'DROP_GET_OR_CREATE_CUSTOMER','err'))
      user,_new = f({'email': request.POST['email']})
      order.user = user
      order.save()
    if user:
      kwargs['customer'] = customer = Customer.get_or_create(user)[0]
      token = kwargs.pop('source')
    try:
      # both these could cause cards to be declines, so they both need to be in here
      if customer:
        card = customer.add_card(token)
      charge = stripe.Charge.create(**kwargs)
    except stripe.error.CardError,e:
      raise PaymentError(e)
    if card:
      card.remove()
  def refund(self,transaction_id):
    #! TODO needs error catching
    return stripe.Refund.create(charge=transaction_id).id
