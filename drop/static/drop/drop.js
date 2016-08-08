uR.drop = (function() {
  uR.ajax({
    url: '/drop/products.js',
    success: function(data) {
      uR.drop.products = {};
      uR.forEach(data.products,function(product) { uR.drop.products[product.id] = product });
    }
  });
  function addToCart(form) {
    uR.ajax({
      form: form,
      success: function(data) {
        uR.drop.cart = data.cart;
        uR.mountElement("shopping-cart",{mount_to:"#alertdiv"});
      }
    });
  }
  return {
    addToCart: addToCart,
  };
})()
