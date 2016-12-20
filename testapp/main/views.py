from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

def home(request):
  return TemplateResponse(request,"index.html",{})

def direct_to_template(request,template,context={}):
  return TemplateResponse(request,template,context)

redirect = lambda request,url: HttpResponseRedirect(url)
