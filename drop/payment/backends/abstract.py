

class PaymentBackend(object):
  """
  A shell api to guide other backends
  """
  def charge(self,order,**kwargs):
    pass
  def refund(self,order,**kwargs):
    pass
