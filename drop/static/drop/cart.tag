(function() {
  uR.drop._addToCart = {}
})();

<add-to-cart>
  <div if={ !opts.hide_price }>
    <div class="pre-sale" if={ product.sale_price != product.price }>${ product.price.toFixed(2) }</div>
    <div class="price">${ product.sale_price.toFixed(2) }</div>
  </div>
  <button class={ btn_class } onclick={ addToCart } if={ !in_cart }>{ add_text }</button>
  <button class={ btn_class } onclick={ uR.drop.openCart } if={ in_cart }>{ show_text }</button>

  var self = this;
  this.target = this.root;
  this.on("mount",function() {
    this.add_text = this.opts.add_text || "Add to Cart";
    this.show_text = this.opts.show_text || "View in Cart";
    this.product = uR.drop.products[this.opts.product_id];
    if (!this.product) { return this.unmount() }
    this.btn_class = this.opts.btn_class || uR.config.btn_primary;
    if (this.opts.root_class) { this.root.classList.add(this.opts.root_class); }
    this.update();
  });
  this.on("update",function() {
    this.in_cart = false;
    uR.forEach(uR.drop.cart.all_items,function(item) {
      if (self.opts.product_id == item.product_id) { self.in_cart = true }
    })
  });
  addToCart() {
    if (uR.drop._addToCart[this.product.model_slug]) {
      uR.drop._addToCart[this.product.model_slug]({product: this.product});
    } else { uR.drop.saveCartItem(this.opts.product_id,this.opts.quantity || 1,this) }
  }
</add-to-cart>

<cart-button>
  <button class={ uR.config.btn_primary } onclick={ uR.drop.openCart }>
    <i class="fa fa-shopping-cart"></i>
    { uR.drop.cart.all_items.length } items ${ total_price.toFixed(2) }
  </button>

  this.on("update",function() {
    this.total_price = parseFloat(uR.drop && uR.drop.cart && uR.drop.cart.total_price);
    if (!this.total_price) { this.root.style.display = "none"; }
    else { this.root.style = "block"; }
  })
</cart-button>

<shopping-cart>
  <div class={ theme.outer } name="ajax_target">
    <div class={ theme.header }>
      <h3>Shopping Cart</h3>
    </div>
    <div class={ theme.content }>
      <div if={ !uR.drop.cart.all_items.length }>
        Your cart is empty. Please close me. Thank you.
      </div>
      <div if={ uR.drop.cart.all_items.length }>
        <div class={ uR.theme.cart_items }>
          <div class="item" each={ uR.drop.cart.all_items }>
            <div class="name">
              <b>{ display_name }</b> { after }<br/>
              <a class="remove" onclick={ parent.remove }>Remove</a>
            </div>
            <div class="price-box" if={ has_quantity }>
              <div class="unit-price"> ${ unit_price }</div>
              <div class="quantity">
                <a class="fa fa-plus-circle increment" onclick={ parent.plusOne }></a>
                <a class="fa fa-minus-circle decrement" onclick={ parent.minusOne }></a>
                <i class="fa fa-times"></i> { quantity }
              </div>
              <span class="total">${ line_subtotal }</span>
            </div>
            <div if={ !has_quantity } class="price-box">
              <span class="total">${ line_subtotal }</span>
              <div if={ has_widget }>
                <a onclick={ parent.editCartItem }><i class="fa fa-edit"></i> edit</a>
              </div>
            </div>
            <div class="extra_price_field" each={ field in extra_price_fields }>
              <div class="description">{ field[0] }</div>
              <div class="amount">${ field[1] }</div>
            </div>
          </div>
        </div>
        <div class="checkout-box">
          <div class="subtotals"></div>
          Order Total: <b>${ uR.drop.cart.total_price }</b>
        </div>
        <div class={ uR.theme.error_class } style="margin:10px 0 0" each={ n,i in errors }>{ n }</div>
      </div>
    </div>
    <div class="{ theme.footer } valign-wrapper" if={ !uR.drop.cart.all_items.length }>
      <button class={ uR.config.btn_cancel } onclick={ close }>Close</button>
    </div>
    <div class="{ theme.footer } valign-wrapper" if={ uR.drop.cart.all_items.length }>
      <div class="shipping_choice" if={ requires_shipping }>
        <div if={ !shipping_address }>
          <button class={ uR.config.btn_primary } onclick={ selectShipping }>Checkout</button>
        </div>
        <div if={ shipping_address }>
          <div>
            <h5>Ship to:</h5>
            { shipping_address.name }<br/>
            { shipping_address.address }<br/>
            { shipping_address.city }
          </div>
          <div>
            <button class={ uR.config.btn_primary } onclick={ selectShipping }>Change Shipping Address</button>
          </div>
        </div>
      </div>
      <div class="payment_buttons" if={ checkoutReady }>
        <button each={ backends } onclick={ parent.checkout } class={ className } alt={ copy }>{ copy }</button>
        <a onclick={ close }>&laquo; Keep Shopping</a>
      </div>
    </div>
  </div>

  var self = this;
  this.backends = [ //#! TODO should be uR.drop.payment_backends and should be derived from server
    { tagname: 'stripe-checkout', copy: "Pay with Credit Card", className: uR.config.btn_primary },
    { tagname: 'paypal-checkout', copy: "Pay with Paypal", className: "paypal_button or" },
  ]
  this.on("update",function() {
    self.target = self.root.querySelector(".card");
    uR.forEach(uR.drop.cart.all_items,function(item) {
      var product = uR.drop.products[item.product_id];
      item.display_name = product.display_name;
      item.unit_price = product.unit_price;
      item.has_quantity = product.has_quantity;
      self.requires_shipping = self.requires_shipping || product.requires_shipping;
      item.has_widget = uR.drop._addToCart[product.model_slug];
      item.model_slug = product.model_slug;
    });
    self.checkoutReady = true;
    this.shipping_address = this.opts.selected_address;
    if (self.requires_shipping && !self.shipping_address) { self.checkoutReady = false }
    riot.update("cart-button");
  });

  close(e) {
    this.unmount();
  }
  saveCart(e) {
    uR.drop.saveCartItem(e.item.product_id,e.item.quantity,this);
  }
  plusOne(e) {
    e.item.quantity++;
    this.saveCart(e);
  }
  minusOne(e) {
    e.item.quantity--;
    this.saveCart(e);
  }
  remove(e) {
    e.item.quantity=0;
    this.saveCart(e);
  }
  selectShipping(e) {
    uR.alertElement('select-address',{success: uR.drop.openCart});
  }
  checkout(e) {
    this.errors = undefined;
    uR.drop.ajax({
      url: "/ajax/start_checkout/",
      that: this,
      success: function(data) { uR.alertElement(e.item.tagname,data); },
      error: function(data) { self.errors = data.errors },
    });
  }
  if (uR.drop.login_required) {
    this.checkout = uR.auth.loginRequired(this.checkout)
    this.selectShipping = uR.auth.loginRequired(this.selectShipping);
  }
  editCartItem(e) {
    uR.drop._addToCart[e.item.model_slug]({product:uR.drop.products[e.item.product_id],initial:e.item.extra});
  }
</shopping-cart>

<stripe-checkout>
  <div class={ theme.outer }>
    <div class={ theme.header }>
      <h3>Checkout with Stripe</h3>
    </div>
    <div class={ theme.content }>
      <ur-form schema={ schema } initial={ initial } success_text="Pay ${ uR.drop.cart.total_price }">
        <yield to="button_div">
          <div class="stripe_logo"></div>
        </yield>
      </ur-form>
    </div>
  </div>

  var self = this;
  this.schema = [
    {
      name: 'number', label: "Credit Card Number", type: "tel",
      onMount: function() { $("stripe-checkout [name=number]").payment("formatCardNumber"); }
    },
    { name: 'expiry', label: "Expiration Date", max_length: 2,
      onMount: function() { $("stripe-checkout [name=expiry]").payment("formatCardExpiry"); }
    },
    {
      name: 'cvc', label: "CVC Code",
      onMount: function() { $("stripe-checkout [name=cvc]").payment("formatCardCVC"); }
    },
  ];
  if (!uR.auth.user) {
    // stripe doesn't give us email, so we need it
    this.schema.push({'name': 'email', type: 'email', label: 'Email Address'})
  }
  if (uR.DEBUG && window.location.search.indexOf("cheat") != -1) {
    this.initial = {number: "4111 1111 1111 1111", cvc: '123', exp_month: "01", exp_year: "2019" }
  }
  submit(ur_form) {
    self.error = undefined;
    self.root.querySelector("ur-form").setAttribute("data-loading","spinner");
    var data = ur_form.getData();
    var expiry = data.expiry.replace(/ /g,"").split("/");
    data.exp_month = expiry[0];
    data.exp_year = expiry[1];
    self.email = data.email;
    delete data.email; delete data.expiry;
    Stripe.card.createToken(data,this.stripeResponseHandler)
  }
  setError(error) {
    var ur_form = self.tags['ur-form'];
    ur_form.non_field_error = "An error occurred while processing your payment";
    if (error) { ur_form.non_field_error += ": "+ error }
    ur_form.update();
  }
  this.stripeResponseHandler = function(status,response) {
    var target = self.root.querySelector("ur-form");
    if (response.error) {
      target.removeAttribute('data-loading');
      self.setError(response.error.message);
      return;
    }
    uR.drop.ajax({
      method: "POST",
      url: "/stripe/payment/",
      data: {token: response.id,total:uR.drop.cart.total_price,email: self.email},
      target: target,
      success: function(data) {
        target.setAttribute("data-loading","spinner");
        window.location = data.next;
      },
      error: function(data) { self.setError(data.error); }
    });
  }
  close(e) {
    this.unmount();
  }
</stripe-checkout>

<paypal-checkout>
  <div class="target { theme.outer }">
    <form action="https://www.paypal.com/cgi-bin/webscr" method="POST">
      <input name="business" type="hidden" value="{ uR.drop.paypal_email }">
      <span each={ n,i in uR.drop.cart.all_items }>
        <input name="item_name_{ i+1 }" type="hidden" value="{ n.display_name }">
        <input name="item_number_{ i+1 }" type="hidden" value="{ n.product_id }">
        <input name="quantity_{ i+1 }" type="hidden" value="{ n.quantity }">
        <input name="amount_{ i+1 }" type="hidden" value="{ n.line_total }">
      </span>
      <input name="notify_url" type="hidden" value="{ SHOP.base_url}/tx/rx/ipn/handler/">
      <input name="cancel_return" type="hidden" value="{ SHOP.base_url }/shop/">
      <input name="return" type="hidden" value="{ SHOP.base_url }/shop/">
      <input name="invoice" type="hidden" value={ opts.order_id }>
      <input name="cmd" type="hidden" value="_cart">
      <input type="hidden" name="upload" value="1">
      <input type="hidden" name="tax_cart" value="0">
      <input name="charset" type="hidden" value="utf-8">
      <input name="currency_code" type="hidden" value="USD">
      <input name="no_shipping" type="hidden" value="1">
    </form>
    <div class={ theme.content }>
      Redirecting to PayPal to complete transaction.
    </div>
  </div>

  this.on("mount",function() {
    this.update();
    this.root.querySelector(".target").setAttribute("data-loading",uR.config.loading_attribute);
    this.root.querySelector("form").submit();
  });
</paypal-checkout>
