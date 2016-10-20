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
        uR.forEach(data.products,function(product) {
          uR.drop.products[product.id] = product;
          product.price = product.sale_price = parseFloat(product.unit_price);
        });
        uR.drop.discounts = data.discounts;
        uR.forEach(data.discounts,function(discount) {
          uR.forEach(discount.product_ids, function(product_id) {
            var product = uR.drop.products[product_id];
            var discount_price = product.price*(1-discount.percentage/100)
            if (product.sale_price > discount_price) {
              product.discount = discount;
              product.sale_price = discount_price;
            }
          });
        });
      }
    });
  }
  function updateCart() {
    uR.drop.ajax({
      url: '/cart.js',
      success: function(data) { uR.drop.cart = data; },
    });
  }
  function saveCartItem(product_id,quantity,riot_tag) {
    uR.drop.ajax({
      url: "/ajax/edit/",
      that: riot_tag,
      data: { id: product_id, quantity: quantity },
      success: function(data) {
        uR.drop.cart = data.cart;
        riot_tag && riot_tag.update();
      },
      method: "POST",
    });
  }
  function openCart() {
    uR.mountElement(uR.drop.cart_tag,{mount_to:uR.config.mount_alerts_to});
  }
  function updateTags() {
    if (!uR.drop.products || !uR.drop.cart) { return }
    if (!uR.drop._mounted) {
      riot.mount(uR.drop.store_tags);
      uR.drop._mounted = true;
    } else {
      riot.update(uR.drop.store_tags);
    }
  }
  uR.drop = {
    saveCartItem: saveCartItem,
    updateProducts: updateProducts,
    updateCart: updateCart,
    updateTags: uR.debounce(updateTags,100),
    store_tags: "cart-button,add-to-cart",
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
