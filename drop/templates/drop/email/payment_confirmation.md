Dear {{ order.get_user_display }},

Thank you for ordering with {{ settings.SITE_NAME }}. Full details of your order are attached below.

### Order Details

{% include "drop/_order_table.html" %}

### Payment Details

{% include "drop/_payment_table.html" %}

-------

