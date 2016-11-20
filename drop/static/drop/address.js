(function() {
  uR.addRoutes({
    "/select-address/": uR.auth.loginRequired("select-address"),
  });
})()
