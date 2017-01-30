# -*- coding: utf-8 -*-
from drop.models.cartmodel import Cart
from django.contrib.auth.models import AnonymousUser

def get_cart_from_database(request):
    try:
        return Cart.objects.filter(user=request.user)[0]
    except IndexError:
        pass

def get_cart_from_session(request):
    session_cart = None
    session = getattr(request, 'session', None)
    if session is not None:
        cart_id = session.get('cart_id')
        if cart_id:
            try:
                session_cart = Cart.objects.get(pk=cart_id)
            except Cart.DoesNotExist:
                session_cart = None
    return session_cart

def get_or_create_cart(request, save=False):
    """
    Return cart for current visitor.

    For a logged in user, try to get the cart from the database. If it's not there or it's empty,
    use the cart from the session.
    If the user is not logged in use the cart from the session.
    If there is no cart object in the database or session, create one.

    If ``save`` is True, cart object will be explicitly saved.
    """
    if hasattr(request, '_cart'):
        return request._cart
    cart = get_cart_from_session(request)

    if request.user.is_authenticated():
        # if we are authenticated
        if cart and cart.user == request.user:
            # and the session cart already belongs to us, we are done
            pass
        elif cart and not cart.is_empty and cart.user != request.user:
            # if it does not belong to us yet
            database_cart = get_cart_from_database(request)
            if database_cart:
                # and there already is a cart that belongs to us in the database
                # delete the old database cart
                database_cart.delete()
            # save the user to the new one from the session
            cart.user = request.user
            cart.save()
        else:
            # if there is no cart, or it's empty, use the database cart
            cart = get_cart_from_database(request)

    if not cart:
        # in case it's our first visit and no cart was created yet
        if request.user.is_authenticated():
            cart = Cart(user=request.user)
        else:
            cart = Cart()

    if save and not cart.pk:
        cart.save()
    if cart.pk:
        request.session['cart_id'] = cart.pk

    setattr(request, '_cart', cart)

    return request._cart
