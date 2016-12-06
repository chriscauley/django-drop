from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from drop.giftcard.models import Credit

class Command(BaseCommand):
  def handle(self, *args, **options):
    to_send = Credit.objects.filter(delivery_date__lte=timezone.now(),delivered__isnull=True)
    print "Sending %s giftcard credits"%to_send.count()
    for credit in to_send:
      credit.send()
