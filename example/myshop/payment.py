from django.urls import re_path
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from drop.util.decorators import on_method, drop_login_required, order_required


class ExamplePayment(object):
    backend_name = "Example payment"
    backend_verbose_name = _("Example payment")
    url_namespace = "example-payment"

    def __init__(self, drop):
        self.drop = drop
        self.template = 'mydrop/example_payment.html'

    @on_method(drop_login_required)
    @on_method(order_required)
    def show_payment(self, request):
        if request.POST:
            return self.process_payment(request)

        the_order = self.drop.get_order(request)
        ctx = {
            'order': the_order,
        }
        return render(request, self.template, ctx)

    @on_method(drop_login_required)
    @on_method(order_required)
    def process_payment(self, request):
        the_order = self.drop.get_order(request)
        self.drop.confirm_payment(
            the_order, self.drop.get_order_total(the_order), "None",
            self.backend_name)
        return HttpResponseRedirect(self.drop.get_finished_url())

    def get_urls(self):
        urlpatterns = [
            re_path(r'^$', self.show_payment, name='example-payment'),
            re_path(r'^$', self.process_payment, name='process-payment'),
        ]
        return urlpatterns
