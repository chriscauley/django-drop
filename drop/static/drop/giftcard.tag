uR.ready(function() {
  uR.schema.fields.amount = { type: 'number', extra_attrs: { step: 1 } };
  uR.schema.fields.delivery_date = { type: 'date' };
  uR.schema.fields.recipient_email = { type: 'email' };
  uR.drop._addToCart['giftcard.giftcardproduct'] = function(data) {
    uR.alertElement('purchase-giftcard',data);
  }
  var o = {
    tagname: 'giftcard-checkout', copy: 'Pay with Gift Card Balance', className: uR.config.btn_primary,
  }
  uR.drop.payment_backends.push(o);
});

<purchase-giftcard>
  <div class={ theme.outer }>
    <div class={ theme.header }><h3>Purchase a gift card</h3></div>
    <div class={ theme.content }>
      <ur-form schema={ product.extra_fields } success_text="Add to Cart" initial={ initial }></ur-form>
    </div>
  </div>

  var self = this;
  this.product = this.opts.product;
  this.initial = { };
  if (window.moment) { this.initial.delivery_date = window.moment().format("YYYY-MM-DD"); }
  if (uR.auth.user) {
    this.initial.recipient_name = uR.auth.user.username;
    this.initial.recipient_email = uR.auth.user.email;
  };
  if (uR.drop.product_on_page) { this.initial.amount = parseInt(uR.drop.product_on_page.unit_price); }
  if (this.opts.initial) { this.initial = this.opts.initial; }
  this.submit = function(ur_form) {
    data = ur_form.getData();
    uR.drop.saveCartItem(self.product.id,data.amount,self,data);
  }
  this.add_successful = function() {
    self.unmount();
    uR.drop.openCart();
  }
</purchase-giftcard>
