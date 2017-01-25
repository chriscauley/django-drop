DROP_PAYMENT_BACKENDS = [
  'drop.payment.backends.stripe_backend.Stripe',
  'drop.giftcard.backend.GiftCard',
]

DROP_CART_MODIFIERS = [
  'drop.cart.modifiers.partial_payment.PartialPaymentModifier',
  'drop.discount.modifier.UserDiscountCartModifier',
]
