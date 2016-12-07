from django.conf import settings
from django.http import JsonResponse

from .models import Credit, Debit

from lablackey.decorators import auth_required

import decimal

def user_json(request):
  if not request.user.is_authenticated():
    return JsonResponse({'amount': 0})
  credit = sum(Credit.objects.filter(user=request.user).values_list("amount",flat=True) or [0])
  debit = sum(Debit.objects.filter(user=request.user).values_list("amount",flat=True) or [0])
  return JsonResponse({'amount': credit - debit})

@auth_required
def redeem_ajax(request):
  credit = Credit.objects.get(code=request.POST.get('code',None))
  error = None
  if credit.user == request.user:
    error = "You have already redeemed this gift card."
  elif credit.user:
    error = "This gift card has already been redeemed. If you believe this is a mistake, please contact us."
  else:
    credit.user = request.user
    credit.save()
  return JsonResponse({'error': error})

def arst(request):
  records = [c.as_json for c in Credit.objects.filter(user=request.user)]
  records += [d.as_json for d in Debit.objects.filter(user=request.user)]
  records.sort(key=lambda o:o['created'])
