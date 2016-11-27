# -*- coding: utf-8 -*-
"""
Holds all the information relevant to the client (addresses for instance)
"""
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django.conf import settings

BASE_ADDRESS_TEMPLATE = \
_("""Name: %(name)s,
Address: %(address)s
Zip-Code: %(zipcode)s,
City: %(city)s,
State: %(state)s,
Country: %(country)s""")

ADDRESS_TEMPLATE = getattr(settings, 'SHOP_ADDRESS_TEMPLATE',
                           BASE_ADDRESS_TEMPLATE)
COUNTRY_CHOICES = [
    ('US', 'United States of America'),
]

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.CharField(_('Name'), max_length=255)
    address = models.CharField(_('Address'), max_length=255)
    address2 = models.CharField(_('Address2'), max_length=255, blank=True)
    zip_code = models.CharField(_('Zip Code'), max_length=20)
    city = models.CharField(_('City'), max_length=20)
    state = models.CharField(_('State'), max_length=255)
    country = models.CharField(max_length=2,choices=COUNTRY_CHOICES,default="US")
    schema_exclude = ['user']

    class Meta(object):
        verbose_name = _('Address')
        verbose_name_plural = _("Addresses")

    def __unicode__(self):
        return '%s (%s, %s)' % (self.name, self.zip_code, self.city)

    def clone(self):
        new_kwargs = dict([(fld.name, getattr(self, fld.name))
                           for fld in self._meta.fields if fld.name != 'id'])
        return self.__class__.objects.create(**new_kwargs)

    def as_text(self):
        a = self.address
        if self.address2:
            a += "\n"+self.address2
        return ADDRESS_TEMPLATE % {
            'name': self.name,
            'address': a,
            'zipcode': self.zip_code,
            'city': self.city,
            'state': self.state,
            'country': self.country,
        }
