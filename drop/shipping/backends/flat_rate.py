# -*- coding: utf-8 -*-
from decimal import Decimal

from django.conf import settings
from django.conf.urls import patterns, url
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from drop.util.decorators import on_method, drop_login_required, order_required


class FlatRateShipping(object):
    """
    This is just an example of a possible flat-rate shipping module, that
    charges a flat rate defined in settings.DROP_SHIPPING_FLAT_RATE
    """
    url_namespace = 'flat'
    backend_name = 'Flat rate'
    backend_verbose_name = _('Flat rate')

    def __init__(self, drop):
        self.drop = drop  # This is the drop reference, it allows this backend
        # to interact with it in a tidy way (look ma', no imports!)
        self.rate = getattr(settings, 'DROP_SHIPPING_FLAT_RATE', '10')

    @on_method(drop_login_required)
    @on_method(order_required)
    def view_process_order(self, request):
        """
        A simple (not class-based) view to process an order.

        This will be called by the selection view (from the template) to do the
        actual processing of the order (the previous view displayed a summary).

        It calls drop.finished() to go to the next step in the checkout
        process.
        """
        self.drop.add_shipping_costs(self.drop.get_order(request),
                                     'Flat shipping',
                                     Decimal(self.rate))
        return self.drop.finished(self.drop.get_order(request))
        # That's an HttpResponseRedirect

    @on_method(drop_login_required)
    @on_method(order_required)
    def view_display_fees(self, request):
        """
        A simple, normal view that displays a template showing how much the
        shipping will be (it's an example, alright)
        """
        ctx = {}
        ctx.update({'shipping_costs': Decimal(self.rate)})
        return render_to_response('drop/shipping/flat_rate/display_fees.html',
            ctx, context_instance=RequestContext(request))

    def get_urls(self):
        """
        Return the list of URLs defined here.
        """
        urlpatterns = patterns('',
            url(r'^$', self.view_display_fees, name='flat'),
            url(r'^process/$', self.view_process_order, name='flat_process'),
        )
        return urlpatterns
