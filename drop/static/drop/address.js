(function() {
  uR.addRoutes({
    "/select-address/": uR.auth.loginRequired("select-address"),
  });
  uR.getSchema("/api/schema/address.Address/");
})()
