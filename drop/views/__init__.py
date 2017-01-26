# -*- coding: utf-8 -*-
import ajax
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from drop.models.productmodel import Product

# Use django next please to paginate this
def index(request):
    return TemplateResponse(request,"drop/product_list.html",
                            {'object_list':Product.objects.filter(active=True)})

def detail(request,object_id,slug=None):
    obj = get_object_or_404(Product,id=object_id)
    is_staff = request.user.is_authenticated() and request.user.is_staff
    if not (obj.is_visible or is_staff):
        raise Http404()
    values = {'object': obj}
    meta = obj._meta
    templates = ["%s/%s_detail.html"%(meta.app_label,meta.model_name),'drop/product_detail.html']
    return TemplateResponse(request,templates,values)

#! TODO: everything below here should be removed

from django.views.generic import (TemplateView, ListView, DetailView, View)
from django.views.generic.base import TemplateResponseMixin

class DropTemplateView(TemplateView):
    """
    A class-based view for use within the drop (this allows to keep the above
    import magic in only one place)

    As defined by
    http://docs.djangoproject.com/en/dev/topics/class-based-views/

    Stuff defined here (A.K.A this is a documentation proxy for the above
    link):
    ---------------------------------------------------------------------
    self.template_name : Name of the template to use for rendering
    self.get_context_data(): Returns the context {} to render the template with
    self.get(request, *args, **kwargs): called for GET methods
    """


class DropListView(ListView):
    """
    This is just to abstract the "Django version switching magic happening up
    there
    """


class DropDetailView(DetailView):
    """
    This is just to abstract the "Django version switching magic happening up
    there
    """


class DropView(View):
    """
    An abstraction of the basic view
    """


class DropTemplateResponseMixin(TemplateResponseMixin):
    """
    An abstraction to solve the import problem for the template response mixin
    """
