from graphene_django import DjangoObjectType
import graphene

from .models import Address

class AddressNode(DjangoObjectType):  
  class Meta:
    model = Address

class AddressQuery(graphene.AbstractType):
  my_addresses = graphene.List(AddressNode)
  def resolve_my_addresses(self, args, context, info):
    if not context.user.is_authenticated():
      return Address.objects.none()
    return Address.objects.filter(user=context.user)
