from Option import Option

def polute_configuration(configuration):

  opt = Option('Parsing_Errors_Are_Fatal', 'Stop parsing once an error is detected',
               True, bool, 'Parsing Options')
  configuration.add_option(opt)

  opt = Option('Parsing_Show_Debug', 'Display all debug messages while parsing',
               True, bool, 'Parsing Options')
  configuration.add_option(opt)

  opt = Option('Parsing_Show_Warning', 'Display all warnings while parsing',
               True, bool, 'Parsing Options')
  configuration.add_option(opt)

  opt = Option('Parsing_Show_Errors', 'Display all error messages while parsing',
               True, bool, 'Parsing Options')
  configuration.add_option(opt)

  opt = Option('Parsing_Allow_Toplevel_Expressions', 'Allow toplevel expressions',
               True, bool, 'Parsing Options')
  configuration.add_option(opt)

  opt = Option('Parsing_Allow_Leftover_Tokens', 'Allow leftover tokens; Parse as far as possible',
               True, bool, 'Parsing Options')
  configuration.add_option(opt)



  opt = Option('GUI_Error_Window_Height', 'The height of the error window',
               10, int, 'GUI Options')
  configuration.add_option(opt)

