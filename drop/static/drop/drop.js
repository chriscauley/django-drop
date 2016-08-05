uR.drop = (function() {
  uR.ajax({
    url: '/drop/products.js',
    success: function(data) {
      uR.drop.products = {};
      uR.forEach(data.products,function(product) { uR.drop.products[product.id] = product });
    }
  });
  return {};
})()
