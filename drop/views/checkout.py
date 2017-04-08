from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from drop.models import Order

def thank_you(request,order_pk):
    order = get_object_or_404(Order,pk=order_pk)
    if request.user != order.user and not order.check_token(request.GET.get('token',"")):
        order = None
    values = { 'order': order }
    return TemplateResponse(request,'drop/checkout/thank_you.html',values)
