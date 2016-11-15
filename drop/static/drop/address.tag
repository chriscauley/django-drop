<select-address>
  <div each={ addresses } onclick={ selectAddress }>
    { name }<br />
    { address }<br />
    { address2 }<br />
    { city }, { state } { zip_code }<br />
    { country.name }<br />
  </div>
  <ur-form schema={ uR.schema.address_Address } action="/address/add/" method="POST"></ur-form>

  this.on("mount",function() {
    var query = `
    query {
      myAddresses {
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
        console.log(data);
        console.log(self.addresses);
      },
      that: this,
      target: this.root,
    });
  });

</select-address>
