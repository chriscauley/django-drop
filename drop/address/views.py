from django.http import JsonResponse

from .models import Address

from lablackey.decorators import auth_required

@auth_required
def add(request):
  model = Address
  kwargs = { 'user': request.user, }
  for field,fk_model in model._meta.get_fields_with_model():
    if field.name in ["user","id"]:
      continue
    kwargs[field.name] = request.POST.get(field.name,None)
  model.objects.get_or_create(**kwargs)
  return JsonResponse({'success': '%s created successfully'%model._meta.verbose_name})

@auth_required
def select(request):
  pass
