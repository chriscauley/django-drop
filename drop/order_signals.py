import django.dispatch

# Order-related signals

"""Emitted when the Cart was converted to an Order"""
processing = django.dispatch.Signal(providing_args=['order', 'cart'])

"""Emitted when the user is shown the "select a payment method" page """
payment_selection = django.dispatch.Signal(providing_args=['order'])

"""Emitted when the user finished placing his order (regardless of the payment
success or failure)"""
confirmed = django.dispatch.Signal(providing_args=['order'])

"""Emitted when the payment was received for the Order"""
paid = django.dispatch.Signal(providing_args=['order'])

"""Emitted if the payment was refused or other fatal problem"""
refunded = django.dispatch.Signal(providing_args=['order'])

"""Emitted (manually) when the drop clerk or robot shipped the order"""
shipped = django.dispatch.Signal(providing_args=['order'])
