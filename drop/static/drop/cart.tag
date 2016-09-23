<cart-button>
  <button class={ uR.config.btn_primary } onclick={ uR.drop.openCart }>
    <i class="fa fa-shopping-cart"></i>
    { uR.drop.cart.all_items.length } items ${ total_price.toFixed(2) }
  </button>

  this.on("update",function() {
    this.total_price = parseInt(uR.drop && uR.drop.cart && uR.drop.cart.total_price);
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
        <button onclick={ startCheckout } class="right btn blue" alt="Buy it Now">Checkout</button>
      </div>
    </div>
  </dialog>

  var self = this;
  this.on("update",function() {
    this.cart_items = [];
    uR.forEach(uR.drop.cart.all_items,function(product){
      product.total_price = (product.quantity*parseInt(product.unit_price)).toFixed(2);
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
  startCheckout(e) {
    var form = $(e.target).closest('form');
    uR.ajax({
      url: '/start_checkout/',
      success: function(data) {
        if (data.errors.length) {
          self.errors = data.errors;
          self.update();
        } else {
          form.find("[name=invoice]").val(data.order_pk);
          form.submit();
        }
      },
      that: self,
    })
  }
</shopping-cart>
