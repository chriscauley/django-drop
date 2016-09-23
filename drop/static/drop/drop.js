(function() {
  function ajax(options) {
    options.url = uR.drop.prefix + options.url;
    var _success = options.success || function() {};
    options.success = function(data,request) {
      _success(data,request);
      uR.drop.updateTags();
    }
    uR.ajax(options);
  }
  function updateProducts() {
    uR.drop.ajax({
      url: '/products.js',
      success: function(data) {
        uR.drop.products_list = data.products;
        uR.drop.products = {};
        uR.forEach(data.products,function(product) { uR.drop.products[product.id] = product });
      }
    });
  }
  function updateCart() {
    uR.drop.ajax({
      url: '/cart.js',
      success: function(data) {
        uR.drop.cart = data;
      },
    });
  }
  function saveCartItem(product) {
    if (uR.drop.cart.all_items.indexOf(product) == -1) {
      product.price = parseInt(product.unit_price);
      uR.drop.cart.all_items.push(product);
    }
    uR.drop.ajax({
      url: "/ajax/edit/",
      data: {id: product.id, quantity: product.quantity},
      method: "POST",
    });
  }
  function openCart() {
    uR.mountElement(uR.drop.cart_tag,{mount_to:uR.config.mount_alerts_to});
  }
  function updateTags() {
    if (!uR.drop.products || !uR.drop.cart) { return }
    uR.drop.cart.total_price = 0;
    uR.forEach(uR.drop.cart.all_items,function(c,i) {
      if (c.product_id) {
        var p = uR.drop.products[c.product_id];
        p.quantity = c.quantity;
        p.price = parseInt(p.unit_price);
        c = p;
        uR.drop.cart.all_items[i] = c;
      }
      uR.drop.cart.total_price += c.quantity*c.price;
    });
    uR.drop.cart.all_items = uR.drop.cart.all_items.filter(function(c){ return c.quantity; });
    riot.update([uR.drop.cart_tag].join(','));
  }
  uR.drop = {
    saveCartItem: saveCartItem,
    updateProducts: updateProducts,
    updateCart: updateCart,
    updateTags: uR.debounce(updateTags,100),
    openCart: openCart,
    ajax: ajax,
    cart_tag: 'shopping-cart',
    prefix: "",
  };
  uR.ready(function() {
    uR.drop.updateProducts();
    uR.drop.updateCart();
  });
})()
