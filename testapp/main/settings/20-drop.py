def _discount(cart,user):
  if user.username == "give_me_one_dollar_off":
    return ("Dollar off for being a dude",-1)

DROP_USER_DISCOUNT_FUNCTION = _discount
DROP_CART_MODIFIERS = [
  'drop.cart.modifiers.partial_payment.PartialPaymentModifier',
  'drop.discount.modifier.UserDiscountCartModifier',
]
