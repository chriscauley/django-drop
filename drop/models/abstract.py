# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from decimal import Decimal
from distutils.version import LooseVersion
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.aggregates import Sum
from django.template.defaultfilters import slugify
from django.utils.crypto import salted_hmac
from django.utils.translation import ugettext_lazy as _
from polymorphic.models import PolymorphicModel
from drop.cart.modifiers_pool import cart_modifiers_pool
from drop.util.fields import CurrencyField
from drop.util.loader import get_model_string
import django, datetime, jsonfield

from lablackey.utils import get_admin_url
from lablackey.db.models import NamedTreeModel, JsonMixin

import sys

USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

class Category(NamedTreeModel,JsonMixin):
    featured = models.BooleanField(default=False)
    json_fields = ['id','name']
    slug = property(lambda self: slugify(self.name))
    get_absolute_url = lambda self: reverse("category_detail",kwargs={'slug':self.slug,'category_id': self.id})
    def get_ancestors(self):
        out = []
        category = self.parent
        while category:
            out.append(category)
            category = category.parent
        return out
    class Meta:
        ordering = ('order',)

#==============================================================================
# Product
#==============================================================================
class BaseProduct(PolymorphicModel,JsonMixin):
    """
    A basic product for the drop.
    
    Most of the already existing fields here should be generic enough to reside
    on the "base model" and not on an added property.
    """

    name = models.CharField(max_length=255, verbose_name=_('Name'))
    slug = property(lambda self: slugify(self.name))

    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_('Date added'))
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_('Last modified'))
    unit_price = CurrencyField(verbose_name=_('Unit price'),default=0)
    categories = models.ManyToManyField(Category,blank=True)

    json_fields = [
        'display_name','active','date_added','last_modified','unit_price','model_slug','has_quantity',
        'requires_shipping','extra_fields'
    ]
    model_slug = property(lambda self: '%s.%s'%(self._meta.app_label,self._meta.model_name))
    requires_shipping = False
    get_admin_url = get_admin_url
    has_quantity = False
    extra_fields = []
    def get_purchase_error(self,quantity,cart):
        # Overwrite this to check quantity or other availability
        if self.has_quantity and self.in_stock != None and self.in_stock < quantity:
            s = "Sorry, we only have %s in stock of the following item: %s"
            return s%(self.in_stock,self)
    class Meta(object):
        abstract = True
        app_label = 'drop'
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    __unicode__ = lambda self: self.name
    get_absolute_url = lambda self: reverse('product_detail', args=[self.id,self.slug])

    # active controls when things are listed on homepage, the rest are useful to fine tune behavior
    active = models.BooleanField(default=False, verbose_name=_('Active'))
    is_visible = property(lambda self: self.active) #turn on/off detail view
    sold_out = property(lambda self: not self.active) #for front end display of SOLD OUT!
    can_be_added_to_cart = property(lambda self,user=None: self.active) #backend to block adding to cart

    # These functions all do virtually nothing, provited for extensibility
    get_price = lambda self: self.unit_price
    get_name = lambda self: self.name
    display_name = property(lambda self: self.get_name())
    get_product_reference = lambda self: unicode(self.pk)

    # this hook is used to update the quantity of a product, is such a thing exists
    purchase = lambda self,cart_item: None

    # hook to reverse the effects of purchase
    refund = lambda self,order_item: None

    def get_breadcrumbs(self):
        out = []
        categories = self.categories.order_by("-level")
        if not categories:
            return []
        level = categories[0].level
        for category in categories:
            if category.level != level:
                break
            out.append(category)
        out += categories[0].get_ancestors()
        return out[::-1]

#==============================================================================
# Carts
#==============================================================================
class BaseCart(models.Model,JsonMixin):
    """
    This should be a rather simple list of items. 
    
    Ideally it should be bound to a session and not to a User is we want to let 
    people buy from our drop without having to register with us.
    """
    # If the user is null, that means this is used for a session
    user = models.OneToOneField(USER_MODEL, null=True, blank=True)
    session_id = None
    extra_price_fields = []
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    json_fields = ['user_id','session_id','total_price','all_items','extra_price_fields','extra']
    extra = jsonfield.JSONField(default=dict,blank=True)
    all_items = property(lambda self:[c.as_json for c in self._updated_cart_items or []])
    __unicode__ = lambda self: "%s's cart"%self.user

    def get_json(self,request):
        self.update(request)
        return self.as_json

    class Meta(object):
        abstract = True
        app_label = 'drop'
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')

    def __init__(self, *args, **kwargs):
        super(BaseCart, self).__init__(*args, **kwargs)
        # That will hold things like tax totals or total discount
        self.subtotal_price = Decimal('0.0')
        self.total_price = Decimal('0.0')
        self.current_total = Decimal('0.0')  # used by cart modifiers
        self._updated_cart_items = None

    def add_product(self, product, quantity=1, merge=True, queryset=None):
        """
        Adds a (new) product to the cart.

        The parameter `merge` controls whether we should merge the added
        CartItem with another already existing sharing the same
        product_id. This is useful when you have products with variations
        (for example), and you don't want to have your products merge (to loose
        their specific variations, for example).

        A drawback is that generally  setting `merge` to ``False`` for
        products with variations can be a problem if users can buy thousands of
        products at a time (that would mean we would create thousands of
        CartItems as well which all have the same variation).

        The parameter `queryset` can be used to override the standard queryset
        that is being used to find the CartItem that should be merged into.
        If you use variations, just finding the first CartItem that
        belongs to this cart and the given product is not sufficient. You will
        want to find the CartItem that already has the same variations that the
        user chose for this request.

        Example with merge = True:
        >>> self.items[0] = CartItem.objects.create(..., product=MyProduct())
        >>> self.add_product(MyProduct())
        >>> self.items[0].quantity
        2

        Example with merge=False:
        >>> self.items[0] = CartItem.objects.create(..., product=MyProduct())
        >>> self.add_product(MyProduct())
        >>> self.items[0].quantity
        1
        >>> self.items[1].quantity
        1
        """
        from drop.models import CartItem

        # check if product can be added at all
        if not getattr(product, 'can_be_added_to_cart', True):
            return None

        # get the last updated timestamp
        # also saves cart object if it is not saved
        self.save()

        if queryset is None:
            queryset = CartItem.objects.filter(cart=self, product=product)
        item = queryset
        # Let's see if we already have an Item with the same product ID
        if item.exists() and merge:
            cart_item = item[0]
            cart_item.quantity = cart_item.quantity + int(quantity)
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                cart=self, quantity=quantity, product=product)
            cart_item.save()

        return cart_item

    def update_quantity(self, cart_item_id, quantity):
        """
        Updates the quantity for given cart item or deletes it if its quantity
        reaches `0`
        """
        cart_item = self.items.get(pk=cart_item_id)
        if quantity == 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        self.save()
        return cart_item

    def delete_item(self, cart_item_id):
        """
        A simple convenience method to delete one of the cart's items. 
        
        This allows to implicitely check for "access rights" since we insure the
        cartitem is actually in the user's cart.
        """
        cart_item = self.items.get(pk=cart_item_id)
        cart_item.delete()
        self.save()

    def get_updated_cart_items(self):
        """
        Returns updated cart items after update() has been called and
        cart modifiers have been processed for all cart items.
        """
        assert self._updated_cart_items is not None, ('Cart needs to be '
            'updated before calling get_updated_cart_items.')
        return self._updated_cart_items

    def update(self, request):
        """
        This should be called whenever anything is changed in the cart (added
        or removed).
        
        It will loop on all line items in the cart, and call all the price
        modifiers on each row.
        After doing this, it will compute and update the order's total and
        subtotal fields, along with any payment field added along the way by
        modifiers.

        Note that theses added fields are not stored - we actually want to
        reflect rebate and tax changes on the *cart* items, but we don't want
        that for the order items (since they are legally binding after the
        "purchase" button was pressed)
        """
        from drop.models import CartItem, Product

        # This is a ghetto "select_related" for polymorphic models.
        items = CartItem.objects.filter(cart=self).order_by('pk')
        product_ids = [item.product_id for item in items]
        products = Product.objects.filter(pk__in=product_ids)
        products_dict = dict([(p.pk, p) for p in products])

        self.extra_price_fields = []  # Reset the price fields
        self.subtotal_price = Decimal('0.0')  # Reset the subtotal

        # The request object holds extra information in a dict named 'cart_modifier_state'.
        # Cart modifiers can use this dict to pass arbitrary data from and to each other.
        if not hasattr(request, 'cart_modifier_state'):
            setattr(request, 'cart_modifier_state', {})

        # This calls all the pre_process_cart methods (if any), before the cart
        # is processed. This allows for data collection on the cart for
        # example)
        for modifier in cart_modifiers_pool.get_modifiers_list():
            modifier.pre_process_cart(self, request)

        for item in items:  # For each CartItem (order line)...
            # This is still the ghetto select_related
            item.product = products_dict[item.product_id]
            self.subtotal_price = self.subtotal_price + item.update(request)

        self.current_total = self.subtotal_price
        # Now we have to iterate over the registered modifiers again
        # (unfortunately) to pass them the whole Order this time
        for modifier in cart_modifiers_pool.get_modifiers_list():
            modifier.process_cart(self, request)

        self.total_price = self.current_total

        # This calls the post_process_cart method from cart modifiers, if any.
        # It allows for a last bit of processing on the "finished" cart, before
        # it is displayed
        for modifier in cart_modifiers_pool.get_modifiers_list():
            modifier.post_process_cart(self, request)

        # Cache updated cart items
        self._updated_cart_items = items

    def empty(self):
        """
        Remove all cart items
        """
        if self.pk:
            self.items.all().delete()
            self.delete()

    @property
    def total_quantity(self):
        """
        Returns the total quantity of all items in the cart.
        """
        return sum([ci.quantity for ci in self.items.all()])

    @property
    def is_empty(self):
        return self.total_quantity == 0


class BaseCartItem(models.Model,JsonMixin):
    """
    This is a holder for the quantity of items in the cart and, obviously, a
    pointer to the actual Product being purchased :)
    """
    cart = models.ForeignKey(get_model_string('Cart'), related_name="items")

    quantity = models.IntegerField()

    product = models.ForeignKey(get_model_string('Product'))
    extra = jsonfield.JSONField(default=dict)
    json_fields = ['quantity','product_id','line_subtotal','line_total','extra_price_fields','extra','line_unit_price']

    class Meta(object):
        abstract = True
        app_label = 'drop'
        verbose_name = _('Cart item')
        verbose_name_plural = _('Cart items')

    @property
    def line_unit_price(self):
        return self.line_total/self.quantity

    def __init__(self, *args, **kwargs):
        # That will hold extra fields to display to the user
        # (ex. taxes, discount)
        super(BaseCartItem, self).__init__(*args, **kwargs)
        self.extra_price_fields = []  # list of tuples (label, value)
        # These must not be stored, since their components can be changed
        # between sessions / logins etc...
        self.line_subtotal = Decimal('0.0')
        self.line_total = Decimal('0.0')
        self.current_total = Decimal('0.0')  # Used by cart modifiers

    def update(self, request):
        if not self.product.active:
            if sys.argv[1:2] == ['test']:
                print self.product," is not active!"
            else:
                m = "The following product is no longer active and was removed from your cart: %s"%self.product
                messages.warning(request,m)
            self.delete()
            return 0
        self.extra_price_fields = []  # Reset the price fields
        self.line_subtotal = self.product.get_price() * self.quantity
        self.current_total = self.line_subtotal

        for modifier in cart_modifiers_pool.get_modifiers_list():
            # We now loop over every registered price modifier,
            # most of them will simply add a field to extra_price_fields
            modifier.process_cart_item(self, request)

        #! TODO: this needs documentation
        # basically if this setting is true only allow the largest cart_item discount
        # either the most negative (or the last if equal) modifier will be kept
        if getattr(settings,"DROP_SINGLE_CART_ITEM_DISCOUNT",True):
            costs = []
            discount = None
            for price_field in self.extra_price_fields:
                if price_field[1] >= 0:
                    costs.append(price_field)
                else:
                    if not discount or price_field[1] <= discount[1]:
                        discount = price_field
            self.extra_price_fields = costs
            if discount:
                self.extra_price_fields.append(discount)
        for price_field in self.extra_price_fields:
            self.current_total += price_field[1]
        self.line_total = self.current_total
        return self.line_total


#==============================================================================
# Orders
#==============================================================================
class BaseOrder(models.Model):
    """
    A model representing an Order.

    An order is the "in process" counterpart of the dropping cart, which holds
    stuff like the shipping and billing addresses (copied from the User
    profile) when the Order is first created), list of items, and holds stuff
    like the status, shipping costs, taxes, etc.
    """

    REFUNDED = -10  # Order was canceled via the PaymentAPI
    PROCESSING = 10  # New order, addresses and shipping/payment methods chosen (user is in the shipping backend)
    CONFIRMING = 20  # The order is pending confirmation (user is on the confirm view)
    CONFIRMED = 30  # The order was confirmed (user is in the payment backend)
    PAID = 40  # Payment backend successfully completed
    SHIPPED = 50  # The order was shipped to client

    PAYMENT = 30  # DEPRECATED!

    STATUS_CODES = (
        (PROCESSING, _('Processing')),
        (CONFIRMING, _('Confirming')),
        (CONFIRMED, _('Confirmed')),
        (PAID, _('Paid')),
        (SHIPPED, _('Shipped')),
        (REFUNDED, _('Refunded')),
    )

    # If the user is null, the order was created with a session
    user = models.ForeignKey(USER_MODEL, blank=True, null=True,
            verbose_name=_('User'))
    status = models.IntegerField(choices=STATUS_CODES, default=PROCESSING,
            verbose_name=_('Status'))
    order_subtotal = CurrencyField(verbose_name=_('Order subtotal'))
    order_total = CurrencyField(verbose_name=_('Order Total'))
    shipping_address_text = models.TextField(_('Shipping address'), blank=True, null=True)
    billing_address_text = models.TextField(_('Billing address'), blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True,verbose_name=_('Created'))
    updated = models.DateTimeField(auto_now=True)
    cart_pk = models.PositiveIntegerField(_('Cart primary key'), blank=True, null=True)
    get_admin_url = get_admin_url

    class Meta(object):
        abstract = True
        app_label = 'drop'
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def get_user_display(self):
        if self.user:
            return self.user.get_full_name() or self.user.username

    def __unicode__(self):
        return _('Order ID: %(id)s') % {'id': self.pk}

    def get_absolute_url(self):
        return reverse('order_detail', kwargs={'pk': self.pk})

    def is_paid(self):
        """Has this order been integrally paid for?"""
        return self.amount_paid >= self.order_total

    def get_status_name(self):
        return dict(self.STATUS_CODES)[self.status]

    # these two methods are used to allow non-logged in users to see checkout page
    def make_token(self,ts=None):
        ts = (ts or datetime.date.today()).strftime("%m/%d/%y")
        value = "%s-%s"%(ts,unicode(self))
        return "%s-%s"%(ts,salted_hmac(settings.SECRET_KEY, value).hexdigest()[::2])
    def check_token(self,token):
        if not token:
            return
        ts_str, s = token.split("-")
        ts = datetime.datetime.strptime(ts_str,"%m/%d/%y").date()
        #if (datetime.date.today()-ts).days > 10:
        #    return False
        return self.make_token(ts) == token

    @property
    def amount_paid(self):
        """
        The amount paid is the sum of related orderpayments
        """
        sum_ = self.orderpayment_set.filter(refunded=False).aggregate(sum=Sum('amount'))
        result = sum_.get('sum')
        if result is None:
            result = Decimal(0)
        return result

    @property
    def shipping_costs(self):
        from drop.models import ExtraOrderPriceField
        sum_ = Decimal('0.0')
        cost_list = ExtraOrderPriceField.objects.filter(order=self).filter(
                is_shipping=True)
        for cost in cost_list:
            sum_ += cost.value
        return sum_

    @property
    def short_name(self):
        """
        A short name for the order, to be displayed on the payment processor's
        website. Should be human-readable, as much as possible.
        """
        return "%s-%s" % (self.pk, self.order_total)

    def set_billing_address(self, billing_address):
        """
        Process billing_address trying to get as_text method from address
        and copying.
        You can override this method to process address more granulary
        e.g. you can copy address instance and save FK to it in your order
        class.
        """
        if hasattr(billing_address, 'as_text') and callable(billing_address.as_text):
            self.billing_address_text = billing_address.as_text()
            self.save()

    def set_shipping_address(self, shipping_address):
        """
        Process shipping_address trying to get as_text method from address
        and copying.
        You can override this method to process address more granulary
        e.g. you can copy address instance and save FK to it in your order
        class.
        """
        if hasattr(shipping_address, 'as_text') and callable(shipping_address.as_text):
            self.shipping_address_text = shipping_address.as_text()
            self.save()


# We need some magic to support django < 1.3 that has no support
# models.on_delete option
f_kwargs = {}
if LooseVersion(django.get_version()) >= LooseVersion('1.3'):
    f_kwargs['on_delete'] = models.SET_NULL


class BaseOrderItem(models.Model):
    """
    A line Item for an order.
    """

    order = models.ForeignKey(get_model_string('Order'), related_name='items',
            verbose_name=_('Order'))
    product_reference = models.CharField(max_length=255,
            verbose_name=_('Product reference'))
    product_name = models.CharField(max_length=255, null=True, blank=True,
            verbose_name=_('Product name'))
    product = models.ForeignKey(get_model_string('Product'),
        verbose_name=_('Product'), null=True, blank=True, **f_kwargs)
    unit_price = CurrencyField(verbose_name=_('Unit price'))
    quantity = models.IntegerField(verbose_name=_('Quantity'))
    line_subtotal = CurrencyField(verbose_name=_('Line subtotal'))
    line_total = CurrencyField(verbose_name=_('Line total'))
    extra = jsonfield.JSONField(default=dict)

    class Meta(object):
        abstract = True
        app_label = 'drop'
        verbose_name = _('Order item')
        verbose_name_plural = _('Order items')

    def save(self, *args, **kwargs):
        if not self.product_name and self.product:
            self.product_name = self.product.get_name()
        super(BaseOrderItem, self).save(*args, **kwargs)
