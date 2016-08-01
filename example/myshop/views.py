from django.core.urlresolvers import reverse
from django.views.generic import FormView
from drop.util.order import get_order_from_request
from django import forms
from drop.models import Order

class TermsOfServiceForm(forms.Form):
    agree = forms.BooleanField(required=True, initial=False, label='I agree to the Terms of Service')

class MyOrderConfirmView(FormView):
    template_name = 'mydrop/order_confirm.html'
    form_class = TermsOfServiceForm

    def form_valid(self, form):
        self.confirm_order()
        return super(MyOrderConfirmView, self).form_valid(form)

    def confirm_order(self):
        order = get_order_from_request(self.request)
        order.status = Order.CONFIRMED
        order.save()

    def get_success_url(self):
        return reverse('checkout_payment')

    def get_context_data(self, **kwargs):
        ctx = super(MyOrderConfirmView, self).get_context_data(**kwargs)
        order = get_order_from_request(self.request)
        ctx.update({
            'order': order,
        })
        return ctx
