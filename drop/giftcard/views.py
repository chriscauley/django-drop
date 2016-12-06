from django.http import JsonResponse

def user_credit(request):
  if not request.user.is_authenticated():
    return JsonResponse({'amount': 0})
  credit = sum(request.user.credit_set.all().values_list("amount") or [0])
  debit = sum(request.user.debit_set.all().values_list("amount") or [0])
  return JsonResponse({'amount': credit-debit})
