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
  function addToCart(that) {
    uR.drop.ajax({
      data: { id: that.dataset.id, model: that.dataset.model },
      target: that,
      success: function(data) {
        uR.drop.cart = data.cart;
        uR.drop.openCart();
      }
    });
  }
  function openCart() {
    uR.mountElement(uR.drop.cart_tag,{mount_to:uR.config.mount_alerts_to});
  }
  function updateTags() {
    uR.drop.cart.total = 0;
    if (!uR.drop.products || !uR.drop.cart) { return }
    uR.forEach(uR.drop.cart.all_items,function(c) {
      if (uR.drop.products[c.product_id]) { uR.drop.products[c.product_id].quantity = c.quantity; }
    });
    riot.update([uR.drop.cart_tag].join(','));
  }
  uR.drop = {
    addToCart: addToCart,
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
