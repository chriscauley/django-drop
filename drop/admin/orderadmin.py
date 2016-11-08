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
    raw_id_fields = ('product',)

#TODO: add ExtraOrderItemPriceField inline, ideas?


class OrderAdmin(LocalizeDecimalFieldsMixin, ModelAdmin):
    list_display = ('id', 'user', 'status', 'order_total', 'created')
    list_filter = ('status', 'user')
    search_fields = ('id', 'shipping_address_text', 'user__username')
    date_hierarchy = 'created'
    inlines = (OrderItemInline, OrderExtraInfoInline,
               ExtraOrderPriceFieldInline, OrderPaymentInline)
    readonly_fields = ('created', 'modified', '_status', 'order_total', 'order_subtotal')
    raw_id_fields = ('user',)
    fieldsets = (
        (None, {'fields': ('user', '_status',
                           ('order_total', 'order_subtotal'),
                           ('created', 'modified')
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

ORDER_MODEL = getattr(settings, 'DROP_ORDER_MODEL', None)
if not ORDER_MODEL:
    admin.site.register(Order, OrderAdmin)
