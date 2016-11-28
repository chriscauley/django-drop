<select-address>
  <div each={ addresses } onclick={ selectAddress }>
    { name }<br />
    { address }<br />
    <div if={ address2 }>{ address2 }</div>
    { city }, { state } { zip_code }<br />
    { country.name }<br />
  </div>
  <ur-form schema="/api/schema/address.Address/" action="/address/add/" method="POST"></ur-form>

  this.on("mount", function() {
    var query = `
    query {
      myAddresses {
        id,
        name,
        address,
        address2,
        city,
        state,
        country,
        zipCode,
      }
    }
    `;
    uR.ajax({
      url: "/graphql",
      data: {query: query},
      success: function(data) {
        self.addresses = data.data.myAddresses;
      },
      that: this,
      target: this.root,
    });
  });
  this.ajax_success = function(data,request) {
    if (this.opts.post_to) {
      uR.ajax({
        url: this.opts.post_to,
        method: "POST",
        data: data,
      });
    }
    if (this.opts.success) { this.opts.success({selected_address: data}) }
  }
  selectAddress(e) {
    this.ajax_success(e.item);
  }

</select-address>
