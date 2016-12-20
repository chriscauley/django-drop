from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Credit, Debit

from lablackey.decorators import auth_required

import decimal

def user_json(request):
  if not request.user.is_authenticated():
    return JsonResponse({'amount': 0})
  credit = sum(Credit.objects.filter(user=request.user).values_list("amount",flat=True) or [0])
  debit = sum(Debit.objects.filter(user=request.user).values_list("amount",flat=True) or [0])
  return JsonResponse({'amount': credit - debit})

def redeem_ajax(request):
  credit = Credit.objects.get(code__iexact=request.POST.get('code',None))
  error = None
  if credit.remaining <= 0:
    return JsonResponse({'error': "This gift card has already been redeemed."})
  return JsonResponse({'giftcard': credit.as_json})

def arst(request):
  records = [c.as_json for c in Credit.objects.filter(user=request.user)]
  records += [d.as_json for d in Debit.objects.filter(user=request.user)]
  records.sort(key=lambda o:o['created'])

def validate(request):
  credit = get_object_or_404(Credit,code=request.GET.get('code',None))
  return JsonResponse({'giftcard': credit.as_json})
