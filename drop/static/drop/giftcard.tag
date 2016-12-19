uR.ready(function() {
  uR.schema.fields.amount = { type: 'number', extra_attrs: { step: 1 } };
  uR.schema.fields.delivery_date = {
    placeholder: "MM/DD/YYYY", validate: function(value,riot_tag) {
      e = "Please enter a date matching MM/DD/YYYY";
      if (!value.match(/[10]?\d\/[0123]?\d\/\d\d\d\d/)) { riot_tag.data_error = e; }
    }
  };
  var code_to_check = uR.getQueryParameter("giftcode") || (uR.storage.get("giftcard") || {}).code;
  if (code_to_check) {
    uR.drop.ajax({
      url: "/giftcard/validate/",
      data: { code: code_to_check},
      success: function(data) {
        uR.storage.set("giftcard",data.giftcard);
      }
    });
  }
  uR.drop.updateGiftcard = function() { uR.drop.ajax({
    url: "/giftcard/user.json",
    success: function(data) { uR.drop.giftcard_balance = parseFloat(data.amount); }
  }); }
  uR.drop.updateGiftcard();
  uR.schema.fields.recipient_email = { type: 'email' };
  uR.drop._addToCart['giftcard.giftcardproduct'] = function(data) { uR.alertElement('purchase-giftcard',data); }
  var o = {
    tagname: 'giftcard-checkout', copy: 'Pay With A Gift Card', className: uR.config.btn_primary, icon: 'fa fa-gift'
  }
  uR.drop.payment_backends.push(o);
  var prefix = uR.drop.prefix+"/giftcard";
  var _routes = {};
  _routes[prefix+"/redeem/"] = uR.auth.loginRequired(function(path,data) {
    uR.alertElement("giftcard-redeem",data);
  });
  uR.addRoutes(_routes);
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
  if (window.moment) { this.initial.delivery_date = window.moment().format("M/D/YYYY"); }
  else {
    var d = new Date();
    this.initial.delivery_date = [d.getMonth(),d.getDate(),d.getFullYear()].join("/");
  }
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

<giftcard-redeem>
  <div class={ theme.outer }>
    <div class={ theme.header }><h3>Redeem a Gift Card</h3></div>
    <div class={ theme.content }>
      <ur-form action={ post_url } method="POST" cancel_function={ close } initial={ initial }></ur-form>
    </div>
  </div>

  this.schema = [{name: "code", label: "Redemption Code"}];
  this.initial = {code: uR.storage.get("giftcode") };
  post_url = uR.drop.prefix+"/giftcard/redeem_ajax/";
</giftcard-redeem>

<giftcard-checkout>
  <div class={ theme.outer }>
    <div class={ theme.header }><h3>Pay with Gift Card</h3></div>
    <div class={ theme.content }>
      <ul>
        <li><b>Gift Card Balance:</b> ${ giftcard.remaining }</li>
        <li><b>Cart Total:</b> ${ uR.drop.cart.total_price }</li>
      </ul>
      <ur-form action={ post_url } method="POST" initial={ initial } success_text="Use Gift Card Balance"
               cancel_text="Back to Cart" cancel_function={ uR.drop.openCart }></ur-form>
    </div>
  </div>

  this.schema = [
    {name: "total", label: "Amount to apply", max: uR.drop.giftcard_balance },
    {name: "code", type: "hidden"},
  ];
  if (!uR.auth.user) { this.schema.push(uR.schema.fields.no_email) }
  if (!uR.storage.get("giftcard")) {
    uR.alertElement("giftcard-redeem");
  }
  this.giftcard = uR.storage.get("giftcard");
  post_url = uR.drop.prefix+"/giftcard/payment/";
  this.initial = {
    total: Math.min(this.giftcard.remaining,parseFloat(uR.drop.cart.total_price)),
    code: this.giftcard.code,
    email: this.giftcard.extra.recipient_email,
  };
  ajax_success(data) {
    window.location = data.next;
  }
</giftcard-checkout>
