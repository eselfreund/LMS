
class Configuration(object):

  def __init__(self):
    self.options = {}

  def add_option(self, option):
    self.options[option.name.lower()] = option

  def get_option(self, name):
    name = name.lower()
    if name in self.options:
      return self.options[name]
    else:
      return None

  def get_option_value(self, name, default = None):
    name = name.lower()
    if name in self.options:
      return self.options[name].value
    else:
      return default

  def report_parsing_debug(self, string, position = (0,0)):
    if not self.get_option('Parsing_Show_Debug', False): return
    print "Parsing Debug (%s):" % str(position), string

  def report_parsing_warning(self, string, position = (0,0)):
    if not self.get_option('Parsing_Show_Warning', False): return
    print "Parsing Warning (%s):" % str(position), string

  def report_parsing_error(self, string, position = (0,0)):
    if not self.get_option('Parsing_Show_Error', True): return
    print "Parsing Error (%s):" % str(position)
    print string
    if self.get_option('Parsing_Errors_Are_Fatal', True):
      assert(0 and "Fatal parsing error\nNote: errors_are_fatal = True!")

