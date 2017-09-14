#-*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from drop.admin.mixins import LocalizeDecimalFieldsMixin
from drop.models.ordermodel import (Order, OrderItem,
        OrderExtraInfo, ExtraOrderPriceField, OrderPayment)
from drop.payment.api import PaymentAPI

from drop.models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    if not settings.DEBUG:
        readonly_fields = ('product','extra','quantity')
    model = CartItem
    has_add_permission = lambda *args,**kwargs: False
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    readonly_fields = ('user','extra_price_fields')
    inlines = [CartItemInline]
    search_fields = getattr(settings,"USER_SEARCH_FIELDS",[])
    def has_change_permission(self,request,obj=None):
        if obj:
            obj.update(request)
        return super(CartAdmin,self).has_change_permission(request,obj)

class OrderExtraInfoInline(admin.TabularInline):
    model = OrderExtraInfo
    extra = 0

class OrderPaymentInline(LocalizeDecimalFieldsMixin, admin.TabularInline):
    model = OrderPayment
    extra = 0

class ExtraOrderPriceFieldInline(LocalizeDecimalFieldsMixin, admin.TabularInline):
    model = ExtraOrderPriceField
    extra = 0

class OrderItemInline(LocalizeDecimalFieldsMixin, admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("_purchased","product_reference","product_name","product","unit_price","quantity","line_subtotal","line_total","extra")
    def _purchased(self,obj):
        if not "purchased_pk" in obj.extra:
            return
        args = obj.extra['purchased_model'].split('.')+[obj.extra['purchased_pk']]
        return ("<a href='/admin/%s/%s/%s/' class='fa fa-edit'></a>"%tuple(args)).lower()
    _purchased.allow_tags = True
    raw_id_fields = ('product',)

#TODO: add ExtraOrderItemPriceField inline, ideas?


class OrderAdmin(LocalizeDecimalFieldsMixin, ModelAdmin):
    list_display = ('id', 'user', 'status', 'order_total', 'created', 'ctypes')
    list_filter = ('status',)
    search_fields = ('id', 'shipping_address_text', 'user__username')
    date_hierarchy = 'created'
    inlines = (OrderItemInline, OrderExtraInfoInline,
               ExtraOrderPriceFieldInline, OrderPaymentInline)
    readonly_fields = ('created', 'updated', '_status', 'order_total', 'order_subtotal')
    raw_id_fields = ('user',)
    fieldsets = (
        (None, {'fields': ('user', '_status','status',
                           ('order_total', 'order_subtotal'),
                           ('created', 'updated')
                       )}),
        (_('Shipping'), {
            'fields': ('shipping_address_text',),
        }),
        (_('Billing'), {
            'fields': ('billing_address_text',)
        }),
    )
    def _status(self,obj=None):
        if obj:
            link = "None"
            if obj.status in [Order.PAID, Order.SHIPPED]:
                link = "<a href='%s'>Refund Order</a>"%reverse("admin:drop_refund_order",args=[obj.id])
            return "%s<br/>Action: %s"%(obj.get_status_display(), link)
    _status.allow_tags = True
    def get_urls(self):
        return [
            url(r'^(\d+)/refund/$',self.admin_site.admin_view(self.refund_view),name='drop_refund_order')
        ] + list(super(OrderAdmin,self).get_urls())
    def refund_view(self,request,order_id):
        model = self.model
        PaymentAPI().refund_order(model.objects.get(id=order_id),request)
        s = "admin:%s_%s_change"%(self.model._meta.app_label,self.model._meta.model_name)
        return HttpResponseRedirect(reverse(s,args=[order_id]))
    def ctypes(self,obj):
        return "<br/>".join([unicode(i.product.polymorphic_ctype_id) for i in obj.items.all() if i.product])
    ctypes.allow_tags = True

ORDER_MODEL = getattr(settings, 'DROP_ORDER_MODEL', None)
if not ORDER_MODEL:
    admin.site.register(Order, OrderAdmin)
