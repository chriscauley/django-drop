from django.urls import re_path

from drop.views.cart import CartDetails, CartItemDetail


urlpatterns = [
    re_path(r'^delete/$', CartDetails.as_view(action='delete'),  # DELETE
        name='cart_delete'),
    re_path(r'^item/$', CartDetails.as_view(action='post'),  # POST
        name='cart_item_add'),
    re_path(r'^$', CartDetails.as_view(), name='cart'),  # GET
    re_path(r'^update/$', CartDetails.as_view(action='put'),
        name='cart_update'),

    # CartItems
    re_path(r'^item/(?P<id>[0-9]+)$', CartItemDetail.as_view(),
        name='cart_item'),
    re_path(r'^item/(?P<id>[0-9]+)/delete$',
        CartItemDetail.as_view(action='delete'),
        name='cart_item_delete'),
]
