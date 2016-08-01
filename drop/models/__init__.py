from django.conf import settings

from cartmodel import *  # NOQA
from ordermodel import *  # NOQA
from productmodel import *  # NOQA
from drop.order_signals import *  # NOQA
from drop.util.loader import load_class

# Load the class specified by the user as the Address Model.
AddressModel = load_class(getattr(settings, 'DROP_ADDRESS_MODEL',
    'drop.addressmodel.models.Address'))
