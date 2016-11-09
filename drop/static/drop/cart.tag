<add-to-cart>
  <div class="pre-sale" if={ product.sale_price != product.price }>${ product.price.toFixed(2) }</div>
  <div class="price">${ product.sale_price.toFixed(2) }</div>
  <button class={ btn_class } onclick={ addToCart } if={ !in_cart }>Add to Cart</button>
  <button class={ btn_class } onclick={ uR.drop.openCart } if={ in_cart }>Show in Cart</button>

  var self = this;
  this.ajax_success = uR.drop.openCart;
  this.target = this.root;
  this.on("mount",function() {
    this.product = uR.drop.products[this.opts.product_id];
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
    uR.drop.saveCartItem(this.opts.product_id,1,this)
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
  <div ur-mask onclick={ close }></div>
  <dialog open class="{ uR.theme.modal_outer }">
    <div class="{ uR.theme.modal_header }">
      <h3>Shopping Cart</h3>
    </div>
    <div class="{ uR.theme.modal_content }">
      <div if={ !uR.drop.cart.all_items.length }>Your cart is empty</div>
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
          </div>
          <div class="extra_price_field" each={ field in extra_price_fields }>
            <div class="description">{ field[0] }</div>
            <div class="amount">{ field[1] }</div>
          </div>
        </div>
      </div>
      <div class="checkout-box">
        <div class="subtotals"></div>
        Order Total: <b>${ uR.drop.cart.total_price }</b>
      </div>
      <div class="alert alert-danger" style="margin:10px 0 0" each={ n,i in errors }>{ n }</div>
    </div>
    <div class="{ uR.theme.modal_footer } valign-wrapper">
      <div class="payment_buttons">
        <button each={ backends } onclick={ parent.checkout } class={ className } alt={ copy }>{ copy }</button>
        <a onclick={ close }>&laquo; Keep Shopping</a>
      </div>
    </div>
  </dialog>

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
    });
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
  checkout(e) {
    uR.alertElement(e.item.tagname);
  }
</shopping-cart>

<stripe-checkout>
  <div ur-mask onclick={ close }></div>
  <dialog open class={ uR.theme.modal_outer }>
    <div class={ uR.theme.modal_header }>
      <a class="close" onclick={ close }>&times;</a>
      <h3>Checkout with Stripe</h3>
    </div>
    <div class={ uR.theme.modal_content }>
      <ur-form schema={ schema } initial={ initial } success_text="Pay ${ uR.drop.cart.total_price }">
        <yield to="button_div">
          <div class="stripe_logo"></div>
        </yield>
      </ur-form>
    </div>
  </dialog>

  var self = this;
  this.schema = [
    {
      name: 'number', label: "Credit Card Number", type: "tel",
      onMount: function() { $("stripe-checkout [name=number]").payment("formatCardNumber"); }
    },
    { name: 'exp_month', label: "Expiration Month", type: "number", max_length: 2 },
    { name: 'exp_year', label: "Expiration Year", type: "number", max_length: 2 },
    {
      name: 'cvc', label: "CVC Code", type: "number",
      //onMount: function() { $("stripe-checkout [name=cvc]").payment("formatCardCVC"); }
    },
    //{ name: 'customer', }
  ];
  if (uR.DEBUG && window.location.search.indexOf("cheat") != -1) {
    this.initial = {number: "4111 1111 1111 1111", cvc: '123', exp_month: "01", exp_year: "2019", customer:'cus_9OVOTsrv4LwJo6' }
  }
  submit(ur_form) {
    self.root.querySelector("ur-form").setAttribute("data-loading","spinner");
    Stripe.card.createToken(ur_form.getData(),this.stripeResponseHandler)
  }
  this.stripeResponseHandler = function(status,response) {
    var ur_form = self.tags['ur-form'];
    var target = self.root.querySelector("ur-form");

    if (response.error) {
      target.removeAttribute('data-loading');
      ur_form.non_field_error = "An error occurred while processing your payment: "+response.error.message;
      ur_form.update()
      return;
    }

    uR.drop.ajax({
      method: "POST",
      url: "/stripe/payment/",
      data: {token: response.id,total:uR.drop.cart.total_price},
      target: target,
      success: function(data) {
        target.setAttribute("data-loading","spinner");
        window.location = data.next;
      },
      error: function(data) { alert('an unknown error has occurred') }
    });
  }
  close(e) {
    this.unmount();
  }
</stripe-checkout>

<paypal-checkout>
  <div ur-mask onclick={ close }></div>
  <dialog open class={ uR.theme.modal_outer }>
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
      <input name="invoice" type="hidden" value={ invoice_id }>
      <input name="cmd" type="hidden" value="_cart">
      <input type="hidden" name="upload" value="1">
      <input type="hidden" name="tax_cart" value="0">
      <input name="charset" type="hidden" value="utf-8">
      <input name="currency_code" type="hidden" value="USD">
      <input name="no_shipping" type="hidden" value="1">
      <input type="submit"/>
    </form>
    <div class={ uR.theme.modal_content }>
      Redirecting to PayPal to complete transaction.
    </div>
  </dialog>

  this.on("mount",function() {
    this.update();
  //this.root.querySelector("dialog").setAttribute("data-loading",uR.config.loading_attribute);
    //this.root.querySelector("form").submit();
  });
</paypal-checkout>
