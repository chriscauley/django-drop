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
  try:
    order = Order.objects.filter(cart_pk=cart.pk,status__lt=Order.PAID)[0]
  except IndexError:
    order = Order.objects.create_from_cart(cart,request)
  order.status = Order.CONFIRMED
  order.save()
  out = {
    'order_pk': order.pk,
    'errors': []
  }
  for item in cart.items.all():
    if item.product.in_stock is None:
      continue
    if item.product.in_stock < item.quantity:
      s = "Sorry, we only have %s in stock of the following item: %s"
      out['errors'].append(s%(item.product.in_stock,item.product))
  return HttpResponse(json.dumps(out))

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
  order = Order.objects.create_from_cart(cart,request)
  if order.order_total != Decimal(request.POST['total']):
    e = "Front end and back end order totals do not match (%s != %s)"
    raise NotImplementedError(e%(order.order_total, Decimal(request.POST['total'])))
  try:
    charge = backend.charge(order,request)
  except PaymentError,e:
    error = "An error made while processing your payment: %s"%e
    return JsonResponse({'errors': {'non_field_error': error}},status=400)
  # empty the related cart                                                                                   
  try:
    Cart.objects.get(pk=order.cart_pk).empty()
  except Cart.DoesNotExist:
    pass
  return JsonResponse({'next': reverse('checkout-thank_you',args=[order.pk])})

from django.dispatch import receiver
from djstripe import signals

from drop.payment.api import PaymentAPI
  
@receiver(signals.WEBHOOK_SIGNALS['charge.succeeded'])
def process(sender,**kwargs):
  amount = kwargs['event'].webhook_message['object']['amount']
  obj_id = kwargs['event'].webhook_message['object']['id']
  metadata = kwargs['event'].webhook_message['object']['metadata']
  if 'order_id' in metadata:
    order = Order.objects.get(pk=metadata['order_id'])
    PaymentAPI().confirm_payment(order, Decimal(amount)/100, obj_id, 'stripe')
