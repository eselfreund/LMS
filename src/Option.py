
class Option(object):

  def __init__(self, name, description, value, typ, category = 'default', prop = None):
    self.name        = name
    self.description = description
    self.value       = value
    self.typ         = typ
    self.category    = category
    self.prop        = prop

  def is_valid(self, value = None):
    try:
      if value:
        self.typ(value)
      else:
        self.typ(self.value)
      return True
    except:
      return False

  def set_prop(self, prop):
    self.prop = prop
    self.prop = self.value

  def set_value(self, value):
    if not self.is_valid(value):
      return False
    self.value = typ(value)
    if self.prop:
      self.prop = value
