from graphene_django import DjangoObjectType
import graphene

from drop.models import Cart, CartItem

class CartNode(DjangoObjectType):
  class Meta:
    model = Cart

class CartItemNode(DjangoObjectType):
  class Meta:
    model = CartItem
