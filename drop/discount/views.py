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
  if promocode.start_date > today:
    return JsonResponse({'error': 'Promocode "%s" not valid until %s'%(code,promocode.start_date)})
  if promocode.expired:
    return JsonResponse({'error': "This promocode expired on %s"%promocode.end_date})

  cart = get_or_create_cart(request)
  cart.extra['promocode'] = promocode.as_json
  cart.save()
  cart.update(request)
  return JsonResponse({'cart': cart.as_json})
