<cart-button>
  <button class="btn blue">
    <i class="fa fa-cart"></i>
    { cart.all_items.length } items ${ cart.total_price }
  </button>

  this.on("mount",function() {
    uR.ajax({
      url: '/drop/ajax/cart.js',
      success: function(data) {
        this.cart = data;
      },
      that: this
    });
  });
</cart-button>

<cart>
  <div class="mask" onclick={ close }></div>
  <div class="content">
    <div class="header">
      <button class="close" onclick={ close }>&times;</button>
      <h4 class="modal-title">Shopping Cart</h4>
    </div>
    <div class="body">
      <div class="well">
        <div if={ !CART }>Your cart is empty</div>
        <div class="items">
          <div class="item" each={ cart_items }>
            <div class="name"><b>{ name }</b> { after }</div>
            <div class="quantity">{ quantity }</div>
            <i class="fa fa-plus-circle increment" onclick={ parent.plusOne }></i>
            <i class="fa fa-minus-circle decrement" onclick={ parent.minusOne }></i>
            <div class="total">${ (quantity*price).toFixed(2) }</div>
            <i class="fa fa-times remove" onclick={ parent.remove }></i>
          </div>
        </div>
      </div>
      <div class="checkout-box">
        <div class="subtotals"></div>
        Order Total: <b>${ total.toFixed(2) }</b>
      </div>
      <div class="alert alert-danger" style="margin:10px 0 0" each={ n,i in errors }>{ n }</div>
    </div>
    <div class="modal-footer">
      <button class="pull-left btn btn-default" data-dismiss="modal" onclick="toggleCourses();">
        &laquo; Keep Shopping</button>
      <button onclick={ startCheckout } alt="Buy it Now">Checkout</button>
    </div>
  </div>

  this.SHOP = window.SHOP;
  var that = this;
  document.body.style.overflowY = document.documentElement.style.overflowY = "hidden";
  document.body.style.paddingRight = "17px";
  document.body.scrolling = "no";
  this.on("update",function() {
    this.cart_items = PRODUCTS.list.filter(function(l){return l.quantity});
    this.total = 0;
    for (var i=0;i<this.cart_items.length;i++) {
      var c = this.cart_items[i];
      this.total += c.quantity*c.price;
    }
    updateCartButton();
  });

  close(e) {
    this.unmount();
    riot.update("*");
    document.body.style.overflowY = document.documentElement.style.overflowY = "";
    document.body.scrolling = "yes";
    document.body.style.paddingRight = "";
  }
  function updateCart(e) {
    $.post(
      '/shop/edit/',
      {pk: e.item.pk,quantity:e.item.quantity}
    );
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
    $.get(
      '/shop/start_checkout/',
      function(data) {
        if (data.errors.length) {
          that.errors = data.errors;
          that.update();
        } else {
          form.find("[name=invoice]").val(data.order_pk);
          form.submit();
        }
      },
      "json"
    )
  }
</cart>
