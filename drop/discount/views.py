from django.http import JsonResponse
from django.utils import timezone

from drop.util.cart import get_or_create_cart
from .models import Promocode

def redeem_ajax(request):
  code = request.GET.get('code',None)
  try:
    promocode = Promocode.objects.get(code__iexact=code)
  except Promocode.DoesNotExist:
    return JsonResponse({'error': "Invalid promocode: %s"%code})
  today = timezone.now().date()
  cart = get_or_create_cart(request)
  if promocode.start_date > today:
    return JsonResponse({'error': 'Promocode "%s" not valid until %s'%(code,promocode.start_date)})
  if promocode.expired:
    return JsonResponse({'error': "This promocode expired on %s"%promocode.end_date})
  if not promocode.reuseable:
    if request.user.is_authenticated() and promocode.promocodeusage_set.filter(order__user=request.user):
      if cart.extra.get('promocode',{}).get("code",None) == promocode.code:
        cart.extra['promocode'] = None
        cart.save()
      return JsonResponse({'error': "You have already used this promocode and it can only be used once per student."})

  cart.extra['promocode'] = promocode.as_json
  cart.save()
  cart.update(request)
  return JsonResponse({'cart': cart.as_json})
