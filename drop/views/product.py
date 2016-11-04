# -*- coding: utf-8 -*-
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from drop.models.productmodel import Product

# Use django next please to paginate this
def index(request):
    return TemplateResponse(request,"drop/product_list.html",
                            {'object_list':Product.objects.filter(active=True)})

def detail(request,object_id,slug=None):
    object = get_object_or_404(Product,id=object_id)
    is_staff = request.user.is_authenticated() and request.user.is_staff
    if not (object.is_visible or is_staff):
        raise Http404()
    values = {'object': object}
    meta = object._meta
    templates = ["%s/%s_detail.html"%(meta.app_label,meta.model_name),'drop/product_detail.html']
    return TemplateResponse(request,templates,values)
