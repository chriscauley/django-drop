uR.ready(function() {
  var code_to_check = uR.getQueryParameter("promocode") || (uR.storage.get("promocode") || {}).code;
  if (code_to_check) {
    var has_promocode = uR.storage.get("promocode");
    uR.drop.ajax({
      url: "/promocode/validate/",
      data: { code: code_to_check},
      success: function(data) {
        if (!data.promocode || !parseFloat(data.promocode.remaining)) {
          uR.storage.set("promocode",null);
        } else {
          uR.storage.set("promocode",data.promocode);
          if (!has_promocode) {
            uR.alert("The following promocode will be applied at checkout: "+data.promocode.description);
          }
        }
      },
      error: function(data) { uR.storage.set("promocode",null); }
    });
  }
  uR.drop.payment_backends.push({
    tagname: 'promocode-redeem',
    get_copy: function() { return uR.drop.promocode?"Change Promocode":'Enter a Promocode'; },
    className: uR.config.btn_primary,
    icon: 'fa fa-tags',
    test: function() { return uR.drop.promocode_active },
    order: 4,
    skip_checkout: true,
  });
  var prefix = uR.drop.prefix+"/promocode";
  var _routes = {};
  _routes[prefix+"/redeem/"] = function(path,data) { uR.alertElement("promocode-redeem",data) }
  uR.addRoutes(_routes);
});

<promocode-redeem>
  <div class={ theme.outer }>
    <div class={ theme.header }><h3>Enter a Promocode</h3></div>
    <div class={ theme.content }>
      <ur-form action={ post_url } method="POST" cancel_function={ close } initial={ initial }
               ajax_success={ ajax_success } if={ !success_message }></ur-form>
      <div if={ success_message }>
        <p class={ uR.config.alert_success }>{ success_message }</p>
        <button class={ uR.config.btn_primary } onclick={ close }>{ close_text }</button>
      </div>
    </div>
  </div>
  var self = this;
  this.schema = [{name: "code", label: "Promoode"}];
  this.initial = { code: uR.storage.get("promocode") };
  this.post_url = uR.drop.prefix+"/promocode/redeem_ajax/";
  var has_cart = uR.drop.cart && uR.drop.cart.all_items && uR.drop.cart.all_items.length;
  this.ajax_success = function(data) {
    uR.storage.set("promocode",data.promocode);
    uR.alert("The following promocode will be applied at checkout: "+data.promocode.description);
    self.update();
  } 
  close(e) {
    has_cart && uR.drop.openCart();
    this.unmount();
  } 
</promocode-redeem>
