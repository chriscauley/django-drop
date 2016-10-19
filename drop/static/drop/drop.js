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
      success: function(data) {
        uR.drop.cart = data;
      },
    });
  }
  function saveCartItem(product,open_cart) {
    if (typeof product == "number") {
      product = uR.drop.products[product];
      if (!product) { alert("Sorry this item is sold out"); return }
      product.quantity = 1;
    }
    uR.drop.cart.all_items = uR.drop.cart.all_items.filter(function(c){ return c.quantity; });
    if (uR.drop.cart.all_items.indexOf(product) == -1) {
      product.price = parseFloat(product.unit_price);
      uR.drop.cart.all_items.push(product);
    }
    uR.drop.ajax({
      url: "/ajax/edit/",
      data: {id: product.id, quantity: product.quantity},
      method: "POST",
    });
    open_cart && uR.drop.openCart();
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
        p.price = parseFloat(p.unit_price);
        c = p;
        uR.drop.cart.all_items[i] = c;
      }
      uR.drop.cart.total_price += c.quantity*c.price;
    });
    uR.drop.cart.all_items = uR.drop.cart.all_items.filter(function(c){ return c.quantity; });
    if (uR.drop._mounted) {
      riot.update([uR.drop.cart_tag].join(','));
    } else {
      riot.mount("cart-button,add-to-cart");
    }
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
