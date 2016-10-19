# -*- coding: utf-8 -*-
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from drop.models.productmodel import Product
from drop.views import (DropListView, DropDetailView)

class ProductListView(DropListView):
    """
    This view handles displaying the product catalogue to customers.
    It filters out inactive products and shows only those that are active.
    """
    generic_template = 'drop/product_list.html'

    def get_queryset(self):
        """
        Return all active products.
        """
        return Product.objects.filter(active=True)

def detail(request,object_id,slug=None):
    object = get_object_or_404(Product,id=object_id)
    is_staff = request.user.is_authenticated() and request.user.is_staff
    if not (object.is_visible or is_staff):
        raise Http404()
    values = {'object': object}
    meta = object._meta
    templates = ["%s/%s_detail.html"%(meta.app_label,meta.model_name),'drop/product_detail.html']
    return TemplateResponse(request,templates,values)
