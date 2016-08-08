<cart-button>
  <button class="btn blue" onclick={ openCart }>
    <i class="fa fa-shopping-cart"></i>
    { cart.all_items.length } items ${ cart.total_price }
  </button>

  this.on("mount",function() {
    uR.ajax({
      url: '/drop/ajax/cart.js',
      success: function(data) { uR.drop.cart = data; },
      that: this
    });
  });
  this.on("update",function() { this.cart = uR.drop.cart; });
  openCart(e) {
    uR.mountElement("shopping-cart",{mount_to:"#alertdiv"})
  }
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
    uR.forEach(uR.drop.cart.all_items,function(item){
      var product = uR.drop.products[item.product_id];
      product.quantity = item.quantity;
      product.total_price = (item.quantity*parseInt(product.unit_price)).toFixed(2);
      self.cart_items.push(product);
    });
    riot.update("cart-button");
  });

  close(e) {
    this.unmount();
    riot.update("*");
  }
  function updateCart(e) {
    uR.ajax({
      url: '/drop/ajax/edit/',
      data: {id: e.item.id,quantity:e.item.quantity,product_model: e.item.model_slug},
      success: function(data) { uR.drop.cart = data.cart; },
      method: "POST",
      that: self,
    });
  }
  plusOne(e) {
    e.item.quantity++;
    updateCart(e);
  }
  minusOne(e) {
    e.item.quantity--;
    updateCart(e);
  }
  remove(e) {
    e.item.quantity = 0;
    updateCart(e);
  }
  startCheckout(e) {
    var form = $(e.target).closest('form');
    uR.ajax({
      url: '/drop/start_checkout/',
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
