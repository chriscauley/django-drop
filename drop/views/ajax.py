from django.apps import apps
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt

from drop.backends_pool import payment_backends
from drop.discount.models import ProductDiscount
from drop.exceptions import PaymentError
from drop.models import CartItem, Order, Product, Cart
from drop.util.cart import get_or_create_cart
from drop.util.loader import load_class

import json, datetime
from decimal import Decimal

DROP = getattr(settings,"DROP",{})

def index(request):
  cart = json.dumps({ci.product_id: ci.quantity for ci in get_or_create_cart(request).items.all()})
  values = {
    'cart': cart
  }
  return TemplateResponse(request,'drop/riot/index.html',values)

if DROP.get('login_required',False):
  index = login_required(index)

def products_json(request):
  return JsonResponse({
    'products': [p.as_json for p in Product.objects.active()],
    'discounts': [d.as_json for d in ProductDiscount.objects.all()],
  })

def cart_json(request):
  cart = get_or_create_cart(request,save=False)
  cart.update(request)
  for item in cart.items.all():
    item.update(request)
  return JsonResponse(cart.get_json(request))

@csrf_exempt
def cart_edit(request):
  cart = get_or_create_cart(request,save=True)
  quantity =  int(request.POST['quantity'])
  product = get_object_or_404(Product,id=request.POST['id'])
  defaults = {'quantity': 0}
  cart_item,new = CartItem.objects.get_or_create(product=product,cart=cart,defaults=defaults)
  for field in product.extra_fields:
    cart_item.extra[field] = request.POST.get(field,cart_item.extra.get(field,None))
  if quantity:
    cart_item.quantity = quantity
    cart_item.save()
  else:
    cart_item.delete()

  cart.update(request)
  return JsonResponse({'cart': cart.get_json(request)})

def start_checkout(request):
  cart = get_or_create_cart(request,save=True)
  cart.update(request)
  order = Order.objects.get_or_create_from_cart(cart,request)
  order.status = Order.CONFIRMED
  order.save()
  out = {
    'order_id': order.id,
    'errors': []
  }
  for item in cart.items.all():
    restriction = item.product.get_purchase_error(item.quantity,cart)
    if restriction:
      out['errors'].append(restriction)
  return JsonResponse(out)

@staff_member_required
@csrf_exempt
def receipts(request):
  if request.POST:
    o = Order.objects.get(pk=request.POST['pk'])
    o.status = int(request.POST['status'])
    o.save()
    now = datetime.datetime.now().strftime("%m/%d/%Y at %H:%M")
    status = "delivered" if o.status == Order.SHIPPED else "outstanding"
    t = "%s marked as %s on %s"%(request.user,status,now)
    o.extra_info.create(text=t)
    return HttpResponseRedirect('.')
  values = {
    'outstanding_orders': Order.objects.filter(status=Order.PAID).order_by("-id"),
    'delivered_orders': Order.objects.filter(status=Order.SHIPPED).order_by("-id")[:10]
  }
  return TemplateResponse(request,'store/receipts.html',values)

@staff_member_required
@csrf_exempt
def admin_page(request):
  values = {}
  return TemplateResponse(request,'store/admin.html',values)

@staff_member_required
def admin_products_json(request):
  extra_fields = ['purchase_url','purchase_domain','purchase_url2','purchase_domain2',
                  'purchase_quantity','in_stock']
  out = {product.pk:{k:getattr(product,k,None) for k in extra_fields}
         for product in Product.objects.filter(active=True)}
  return HttpResponse("window.PRODUCTS_EXTRA = %s;"%json.dumps(out))

@staff_member_required
@csrf_exempt
def admin_add(request):
  quantity = int(request.POST['quantity'])
  product_model = apps.get_model(*request.POST['product_model'].split("."))
  product = get_object_or_404(product_model,pk=request.POST['pk'])
  old = product.in_stock or 0 
  product.in_stock = max(old + quantity,0)
  product.save()
  return HttpResponse(str(product.in_stock))

def payment(request,_backend):
  backend = payment_backends.get(_backend)
  # everything until the try/except should be abstracted elsewhere
  cart = get_or_create_cart(request,save=True)
  cart.update(request)
  order = Order.objects.get_or_create_from_cart(cart,request)
  if not order.user and request.POST.get('email',None):
    f = load_class(getattr(settings, 'DROP_GET_OR_CREATE_CUSTOMER','err'))
    user,_new = f({'email': request.POST['email']})
    order.user = user
    order.save()
  try:
    charge = backend.charge(order,request)
  except ImportError,e:
    return JsonResponse({'error': str(e)},status=400)

  # right now only giftcard supports partial payment
  if _backend != 'giftcard' or order.is_paid():
    # empty the related cart
    try:
      Cart.objects.get(pk=order.cart_pk).empty()
    except Cart.DoesNotExist:
      pass
    order.cart_pk = None
    order.save()
    url = reverse('checkout-thank_you',args=[order.pk])+"?token="+order.make_token()
    return JsonResponse({'next': url})
  else:
    return cart_json(request)

# STRIPE LISTENERS
# Move these some place intelligent

from django.dispatch import receiver
import djstripe.signals

from drop.payment.api import PaymentAPI

@receiver(djstripe.signals.WEBHOOK_SIGNALS['charge.succeeded'])
def stripe_payment_successful(sender,**kwargs):
  obj = kwargs['event'].webhook_message['object']
  amount = obj['amount']
  txn_id = obj['id']
  metadata = obj['metadata']
  if 'order_id' in metadata:
    order = Order.objects.get(pk=metadata['order_id'])
    d = "Stripe Payment: {brand} card ending in {last4}".format(**obj['source'])
    PaymentAPI().confirm_payment(order, Decimal(amount)/100, txn_id, 'stripe',d)

# PAYPAL LISTENERS
# Move these some place intelligent

from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged
from django.core.mail import mail_admins
from django.http import QueryDict

from drop.util.loader import load_class

@receiver(payment_was_successful, dispatch_uid='drop.listeners.paypal_payment_successful')
def paypal_payment_successful(sender,**kwargs):
  params = QueryDict(sender.query)

  # for now this is how we differentiate what came from drop
  if not params.get("invoice",None):
    return

  user,new_user = load_class(getattr(settings, 'DROP_GET_OR_CREATE_CUSTOMER','err'))(params)
  # If they're paying us, don't worry about the registration activation process.
  user.active = True
  user.save()
  order = Order.objects.get(pk=params['invoice'])
  if order.user != user:
    if order.user:
      # If it had no user then we're fine, otherwise...
      #! TODO: not sure when this will happen so let's keep an eye on this
      mail_admins("Paypal order jumping users!","%s %s %s %s"%(user,order.user,order,sender))
    order.user = user
    order.save()
  if not "num_cart_items" in params:
    #! TODO this was a problem with the last ipn handler
    mail_admins("No cart items found for %s"%sender.txn_id,"")
  d = "PayPal payment by account: %s"%params.get("payer_email",'UNKNOWN')
  PaymentAPI().confirm_payment(order, Decimal(params['mc_gross']), sender.txn_id, 'paypal',d)

@receiver(payment_was_flagged, dispatch_uid='drop.listeners.paypal_payent_flagged')
def paypal_payment_flagged(sender,**kwargs):
  import sys
  TESTING = sys.argv[1:2] == ['test']

  #sometimes I send bad postbacks in tests that I wish to avoid.
  if not (TESTING and "Invalid postback" in sender.flag_info):
    lines = [
      "%s was flagged and I'd like to know why"%sender,
      'flag: %s'%sender.flag_info
    ]
    mail_admins("paypal flag",'\n'.join(lines))
  paypal_payment_successful(sender,**kwargs)
