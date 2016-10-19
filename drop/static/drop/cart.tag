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
  <div class="mask" onclick={ close }></div>
  <dialog open>
    <a class="close" onclick={ close }>&times;</a>
    <div class="card">
      <div class="card-content">
        <div class="card-title">
          Shopping Cart
        </div>
        <div if={ !cart_items.length }>Your cart is empty</div>
        <div class="items">
          <div class="item" each={ cart_items }>
            <a class="fa fa-times remove" onclick={ parent.remove }></a>
            <div class="name"><b>{ name }</b> { after }</div>
            <div class="quantity">
              { quantity }
              <i class="fa fa-times"></i> { unit_price } =
              <span class="total">${ total_price }</span>
              <a class="fa fa-plus-circle increment" onclick={ parent.plusOne }></a>
              <a class="fa fa-minus-circle decrement" onclick={ parent.minusOne }></a>
            </div>
          </div>
        </div>
        <div class="checkout-box">
          <div class="subtotals"></div>
          Order Total: <b>${ uR.drop.cart.total_price }</b>
        </div>
        <div class="alert alert-danger" style="margin:10px 0 0" each={ n,i in errors }>{ n }</div>
      </div>
      <div class="card-action valign-wrapper">
        <a onclick={ close }>&laquo; Keep Shopping</a>
        <button onclick={ openCheckout } class="right btn blue" alt="Buy it Now">Checkout</button>
      </div>
    </div>
  </dialog>

  var self = this;
  this.on("update",function() {
    this.cart_items = [];
    uR.forEach(uR.drop.cart.all_items,function(product){
      product.total_price = (product.quantity*parseFloat(product.unit_price)).toFixed(2);
      self.cart_items.push(product);
    });
    riot.update("cart-button");
  });

  close(e) {
    this.unmount();
    riot.update("*");
  }
  plusOne(e) {
    e.item.quantity++;
    uR.drop.saveCartItem(e.item);
  }
  minusOne(e) {
    e.item.quantity--;
    uR.drop.saveCartItem(e.item);
  }
  remove(e) {
    e.item.quantity = 0;
    uR.drop.saveCartItem(e.item);
  }
  openCheckout(e) {
    uR.mountElement("checkout-modal",{mount_to:uR.config.mount_alerts_to});
  }
</shopping-cart>

<checkout-modal>
  <div class="mask" onclick={ close }></div>
  <dialog open>
    <div class="card">
      <div class="card-content">
        <ur-form schema={ schema } initial={ initial }></ur-form>
      </div>
    </div>
  </dialog>

  var self = this;
  this.schema = [
    {name: 'number', label: "Credit Card Number", type: "tel"},
    {name: 'cvc', label: "CVC Code", type: "number"},
    {name: 'exp_month', label: "Expiration Month", type: "number",max_length: 2},
    {name: 'exp_year', label: "Expiration Year", type: "number",max_length: 4},
  ];
  if (uR.DEBUG && window.location.search.indexOf("cheat") != -1) {
    this.initial = {number: '4111 1111 1111 1111', cvc: '123', exp_month: '01',exp_year: 2019}
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

    uR.ajax({
      method: "POST",
      url: "/stripe/payment/",
      data: {token: response.id,total:uR.drop.cart.total_price},
      target: target,
      success: function(data) {
        target.setAttribute("data-loading","spinner");
        window.location = data.next;
      }
    });
  }
</checkout-modal>
