from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from drop.views import DropListView, DropDetailView
from drop.models import Order


class OrderListView(DropListView):
    """
    Display list or orders for logged in user.
    """
    queryset = Order.objects.all()

    def get_queryset(self):
        queryset = super(OrderListView, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OrderListView, self).dispatch(*args, **kwargs)


class OrderDetailView(DropDetailView):
    """
    Display order for logged in user.
    """
    queryset = Order.objects.all()

    def get_queryset(self):
        queryset = super(OrderDetailView, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OrderDetailView, self).dispatch(*args, **kwargs)
