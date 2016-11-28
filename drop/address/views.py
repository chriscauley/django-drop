from django.http import JsonResponse
from django.db.models import ManyToOneRel

from .models import Address

from lablackey.decorators import auth_required

@auth_required
def add(request):
  model = Address
  kwargs = { 'user': request.user, }
  for field,fk_model in model._meta.get_fields_with_model():
    if isinstance(field,ManyToOneRel):
      continue
    if field.name in ["user","id"]:
      continue
    kwargs[field.name] = request.POST.get(field.name,None)
  obj,new = model.objects.get_or_create(**kwargs)
  kwargs['id'] = obj.id
  kwargs.pop("user")
  return JsonResponse(kwargs)

@auth_required
def select(request):
  pass
