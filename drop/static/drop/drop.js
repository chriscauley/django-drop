(function() {
  var _ready = [];
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
        uR.drop.ready = function(f) { f(); }
        uR.forEach(_ready, uR.drop.ready)
      }
    });
  }
  function updateCart() {
    uR.drop.ajax({
      url: '/cart.js',
      success: function(data) { uR.drop.cart = data; },
    });
  }
  function saveCartItem(product_id, quantity, riot_tag, data) {
    data = data ||{};
    data.id = product_id;
    data.quantity = quantity;
    uR.drop.ajax({
      url: "/ajax/edit/",
      that: riot_tag,
      data: data,
      success: function(data) {
        uR.drop.cart = data.cart;
        riot_tag && riot_tag.update();
        riot_tag && riot_tag.add_successful && riot_tag.add_successful();
        uR.openCart();
      },
      method: "POST",
    });
  }
  function openCart(data) {
    uR.alertElement(uR.drop.cart_tag,data)
  }
  function updateTags() {
    if (!uR.drop.products_list || !uR.drop.cart) { return }
    uR.forEach(uR.drop.products_list,function (p) { p.quantity = 0; })
    uR.forEach(uR.drop.cart.all_items,function (item) {
      if (uR.drop.products[item.product_id]) { uR.drop.products[item.product_id].quantity = item.quantity; }
    });
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
    modal_cart: true,
    ajax: ajax,
    cart_tag: 'shopping-cart',
    prefix: "",
    ready: function(f) { _ready.push(f) },
    login_required: true
  };
  uR.ready(function() {
    uR.drop.updateProducts();
    uR.drop.updateCart();
    if (uR.drop.login_required) { uR.drop.openCart = uR.auth.loginRequired(openCart) }
  });
})()
