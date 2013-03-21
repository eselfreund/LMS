from AST import *
from Configuration import Configuration

class AbstractParser(object):

  def parse(self, tokens, position):
    assert(0 and "Implement me!")

  def get_token_pos(self, token):
    return (token[2], token[3])

  def get_token_type_and_string(self, token):
    return "%s: %s" % (token[0], token[1])

  def get_next_type(self, tokens, position, expected):
    if len(tokens) <= position:
      return None, position

    if tokens[position][0] == expected:
      return tokens[position], position + 1
    else:
      return None, position

  def get_next_string(self, tokens, position, expected):
    if len(tokens) <= position:
      return None, position

    if tokens[position][1] == expected:
      return tokens[position], position + 1
    else:
      return None, position


class SMLTupleParser(AbstractParser):
  " DONE "
  def __init__(self, configuration, EntryParser, seperator = ","):
    self.configuration = configuration
    self.EntryParser   = EntryParser
    self.seperator     = seperator

  def parse(self, tokens, position, strict = False):
    self.configuration.report_parsing_debug("Start TupleParser (seperator='%s')!\n" % \
        self.seperator, self.get_token_pos(tokens[position]))


    par_open_token, new_position = self.get_next_string(tokens, position, "(")
    if not par_open_token and self.seperator == ",":
      self.configuration.report_parsing_debug("Stop TupleParser, found nothing!",
          self.get_token_pos(tokens[position]))
      return None, position

    entries = []
    while 1:
      entry, new_position = self.EntryParser.parse(tokens, new_position)
      if not entry:
        if self.seperator == ",":
          return None, position
        else:
          assert(self.seperator == "*")
          break

      entries.append(entry)

      par_close_token, new_position = self.get_next_string(tokens, new_position, ")")
      if par_close_token:
        if not par_open_token:
          new_position -= 1
        break

      comma_token, new_position = self.get_next_string(tokens, new_position, self.seperator)
      if not comma_token:
        return None, position

    assert(len(entries) > 0)
    if len(entries) == 1:
      if strict:
        return None, position
      else:
        return entries[0], new_position
    else:
      return ASTTuple(par_open_token, entries, self.seperator), new_position

class SMLTypeParser(AbstractParser):

  def __init__(self, configuration):
    self.configuration    = configuration

  def parse(self, tokens, position, expr, optional = True):

    # check if there are tokens left
    if len(tokens) <= position:
      if optional:
        self.configuration.report_parsing_debug("Stop TypeParser, found no type!(no tokens left!)")
        return expr, position

      else:
        self.configuration.report_parsing_error(
          "Supposed to find a type starting with a colon (':').\n Instead we found '%s @ %s'" % \
                (self.get_token_type_and_string(tokens[position]),
                 str(self.get_token_pos(tokens[position]))))

        self.configuration.report_parsing_debug("Stop TypeParser, found no type!(no tokens left!)")
        return None, position

    self.configuration.report_parsing_debug("Start TypeParser!\n",
        self.get_token_pos(tokens[position]))

    colon_token, new_position = self.get_next_string(tokens, position, ":")
    if colon_token:
      # TODO
      #typ, new_position = self..parse(tokens, new_position)
      if typ:
        expr.add_explicit_typ(typ)
        self.configuration.report_parsing_debug("Stop TypeParser, found %s!" % \
           typ.to_string() , self.get_token_pos(tokens[position]))
        return expr, new_position

    if optional:
      self.configuration.report_parsing_debug("Stop TypeParser, found no type!",
        self.get_token_pos(tokens[position]))
      return expr, position
    else:
      self.configuration.report_parsing_error(
          "Supposed to find a type starting with a colon (':').\n Instead we found '%s @ %s'" % \
                (self.get_token_type_and_string(tokens[position]),
                 str(self.get_token_pos(tokens[position]))))

      self.configuration.report_parsing_debug("Stop TypeParser, found no type!",
        self.get_token_pos(tokens[position]))

      return None, position


class SMLIdentifierGroupParser(AbstractParser):
  " DONE "
  def __init__(self, configuration, seperator = ","):
    self.configuration   = configuration
    self.TupleParser     = SMLTupleParser(configuration, self, seperator = seperator)
    self.seperator       = seperator

  def parse(self, tokens, position):
    self.configuration.report_parsing_debug("Start IdentifierGroupParser (seperator=%s)!\n" %\
        self.seperator, self.get_token_pos(tokens[position]))

    ident_token, new_position = self.get_next_type(tokens, position, "ident")
    if ident_token:
      ident = ASTIdentifier(ident_token)
      ident.is_expression = False
    else:
      ident, new_position = self.TupleParser.parse(tokens, position)

    self.configuration.report_parsing_debug("Stop IdentifierGroupParser, found %s !" % \
        str(ident), self.get_token_pos(tokens[position]))

    return ident, new_position


class SMLExpressionParser(AbstractParser):

  # The order is crucial
  BinaryOperators = [
      ("*", ASTMul, 3, 0), ("/", ASTDiv, 3, 0),
      ("+", ASTPlus, 2, 0), ("-", ASTMinus, 2, 0),
      ("=", ASTEqual, 1, 0), ("<>", ASTNotEqual, 1, 0),
      (">", ASTGreater, 1, 0), ("<", ASTLess, 1, 0),
      ]
  def __init__(self, configuration):
    self.configuration     = configuration
    self.TupleParser       = SMLTupleParser(configuration, self)
    self.conditionalParser = SMLConditionalParser(configuration, self)
    self.TypeParser        = SMLTypeParser(configuration)

  def parse_extended_expressions(self, tokens, position, lhs, precedence = 0):
    if len(tokens) <= position:
      return lhs, position

    application_argument, new_position = self.TupleParser.parse(tokens, position)
    if application_argument:
      application = ASTApplication(lhs, application_argument)
      application, new_position = self.TypeParser.parse(tokens, new_position, application)
      return self.parse_extended_expressions(tokens, new_position, application, 4)

    rhs = None
    hit = True
    new_position = position
    i  = 1
    while hit:
      hit = False
      i+= 1
      for op_string, ASTOpClass, op_pred, op_right in SMLExpressionParser.BinaryOperators:
        op_token, new_position  = self.get_next_string(tokens, new_position, op_string)
        if op_token and op_pred + op_right > precedence:
          rhs, new_position = self.parse_primary(tokens, new_position)
          if not rhs:
            return lhs, position
          rhs_2, new_position_2 = self.parse_extended_expressions(tokens, new_position, rhs, op_pred)
          hit = True
          if rhs_2 and rhs_2 != rhs:
            rhs = rhs_2
            new_position= new_position_2
          lhs = ASTOpClass(op_token, lhs, rhs)
          lhs, new_position = self.TypeParser.parse(tokens, new_position, lhs)
          position = new_position

    return lhs, position

  def parse_primary(self, tokens, position):
    self.configuration.report_parsing_debug("Start PrimaryExpressionParser!\n",
        self.get_token_pos(tokens[position]))
    # Parse 'REAL' tuples of expressions
    #real_tuple_expression, new_position = self.TupleParser.parse(tokens, position, strict = True)
    #if real_tuple_expression:
      #return real_tuple_expression, new_position

    # Parse 'Pseudo' tuples of expressions
    pseudo_tuple_expression, new_position = self.TupleParser.parse(tokens, position)
    if pseudo_tuple_expression:
      self.configuration.report_parsing_debug("\nStop PrimaryExpressionParser, found (pseudo?) tuple expression!",
        self.get_token_pos(tokens[position]))
      return self.TypeParser.parse(tokens, new_position, pseudo_tuple_expression)

    # Parse numbers
    number_token, new_position = self.get_next_type(tokens, position, "number")
    if number_token:
      self.configuration.report_parsing_debug("\nStop PrimaryExpressionParser, found number literal (%s)!" % \
          tokens[position][1], self.get_token_pos(tokens[position]))
      return self.TypeParser.parse(tokens, new_position, ASTNumber(number_token))

    # Parse identifiers
    ident_token, new_position  = self.get_next_type(tokens, position, "ident")
    if ident_token:
      self.configuration.report_parsing_debug("\nStop PrimaryExpressionParser, found identifier (%s)!" % \
          tokens[position][1], self.get_token_pos(tokens[position]))
      return self.TypeParser.parse(tokens, new_position, ASTIdentifier(ident_token))

    # Parse conditionals
    if_token, new_position  = self.get_next_string(tokens, position, "if")
    if if_token:
      conditional, new_position = self.conditionalParser.parse(tokens, position)
      if not conditional:
        return None, position
      self.configuration.report_parsing_debug("\nStop PrimaryExpressionParser, found coniditional!",
           self.get_token_pos(tokens[position]))
      return self.TypeParser.parse(tokens, new_position, coniditional)

    self.configuration.report_parsing_debug("Stop PrimaryExpressionParser, found nothing!",
        self.get_token_pos(tokens[position]))
    return None, position

  def parse(self, tokens, position):
    primary_expression, new_position = self.parse_primary(tokens, position)
    if primary_expression:
      return self.parse_extended_expressions(tokens, new_position, primary_expression)
    return None, position


class SMLConditionalParser(AbstractParser):
  " DONE "
  def __init__(self, configuration, EntryParser):
    self.configuration = configuration
    self.EntryParser   = EntryParser

  def parse(self, tokens, position):
    self.configuration.report_parsing_debug("Start ConditionalParser!\n",
        self.get_token_pos(tokens[position]))

    if_token, new_position  = self.get_next_string(tokens, position, "if")
    if not if_token:
      self.configuration.report_parsing_error(
            "ConditionalParser invoked without 'if' token!\n Instead it found '%s @ %s'" % \
                (self.get_token_type_and_string(tokens[position]),
                 str(self.get_token_pos(tokens[position]))),
            self.get_token_pos(tokens[position]))
      return None, position

    self.configuration.report_parsing_debug(" - ConditionalParser found 'if'",
        self.get_token_pos(tokens[position]))

    guard, new_position = self.EntryParser.parse(tokens, new_position)
    if not guard:
      self.configuration.report_parsing_error(
            "ConditionalParser found 'if' token but no valid expression afterwards!\n Instead it found '%s @ %s'" % \
                (self.get_token_type_and_string(tokens[new_position]),
                 str(self.get_token_pos(tokens[new_position]))))
      return None, position

    self.configuration.report_parsing_debug(" - ConditionalParser found a guard %s"\
         % guard.to_string())

    then_token, new_position  = self.get_next_string(tokens, new_position, "then")
    if not then_token:
      self.configuration.report_parsing_error(
            "ConditionalParser found 'if' token but no matching 'then' token!\n Instead it found '%s @ %s'" % \
                (self.get_token_type_and_string(tokens[new_position]),
                 str(self.get_token_pos(tokens[new_position]))))
      return None, position


    consequence, new_position = self.EntryParser.parse(tokens, new_position)
    if not consequence:
      self.configuration.report_parsing_error(
            "ConditionalParser found 'then' token but no valid expression afterwards!\n Instead it found '%s @ %s'" % \
                (self.get_token_type_and_string(tokens[new_position]),
                 str(self.get_token_pos(tokens[new_position]))))
      return None, position

    self.configuration.report_parsing_debug(" - ConditionalParser found a consequence %s"\
         % consequence.to_string())

    else_token, new_position  = self.get_next_string(tokens, new_position, "else")
    if not else_token:
      self.configuration.report_parsing_error(
            "ConditionalParser found 'if' token and 'then' token but no matching 'else' token!\n Instead it found '%s @ %s'" % \
                (self.get_token_type_and_string(tokens[new_position]),
                 str(self.get_token_pos(tokens[new_position]))))
      return None, position

    alternative, new_position = self.EntryParser.parse(tokens, new_position)
    if not alternative:
      self.configuration.report_parsing_error(
            "ConditionalParser found 'else' token but no valid expression afterwards!\n Instead it found '%s @ %s'" % \
                (self.get_token_type_and_string(tokens[new_position]),
                 str(self.get_token_pos(tokens[new_position]))))
      return None, position

    self.configuration.report_parsing_debug(" - ConditionalParser found an alternative  %s"\
         % alternative.to_string())

    self.configuration.report_parsing_debug("Stop ConditionalParser, found conditional!",
        self.get_token_pos(tokens[position]))
    return ASTConditional(if_token, guard, consequence, alternative), new_position



class SMLDeclarationParser(AbstractParser):
  " DONE "
  def __init__(self, configuration):
    self.configuration = configuration
    self.IdentGroupParser = SMLIdentifierGroupParser(configuration)
    self.ExpressionParser = SMLExpressionParser(configuration)
    self.TypeParser       = SMLTypeParser(configuration)

  def parse(self, tokens, position):
    self.configuration.report_parsing_debug("Start DeclarationParser!\n",
        self.get_token_pos(tokens[position]))

    # Try to parse a 'val-declaration'
    val_token, new_position = self.get_next_string(tokens, position, "val")
    if val_token:
      ident_group, new_position = self.IdentGroupParser.parse(tokens, new_position)
      if not ident_group:
        self.configuration.report_parsing_error(
            "Found val @%s but no identifier(s)!\n Instead '%s @ %s'" % \
                (str(self.get_token_pos(val_token)),
                 self.get_token_type_and_string(tokens[new_position]),
                 str(self.get_token_pos(tokens[new_position]))),
            self.get_token_pos(tokens[new_position]))
        return None, position

      ident_group, new_position = self.TypeParser.parse(tokens, new_position, ident_group)

      equal_token, new_position = self.get_next_string(tokens, new_position, "=")
      if not equal_token:
        self.configuration.report_parsing_error(
            "Found val @%s and identifier(s) but no '='!\n Instead '%s @ %s'" % \
                (str(self.get_token_pos(val_token)),
                 self.get_token_type_and_string(tokens[new_position]),
                 str(self.get_token_pos(tokens[new_position]))),
            self.get_token_pos(tokens[new_position]))
        return None, position

      expression, new_position = self.ExpressionParser.parse(tokens, new_position)
      if not expression:
        self.configuration.report_parsing_error(
            "Found val @%s, identifier(s) and '=' but no valid expression!\n Instead '%s @ %s'" % \
                (str(self.get_token_pos(val_token)),
                 self.get_token_type_and_string(tokens[new_position]),
                 str(self.get_token_pos(tokens[new_position]))),
            self.get_token_pos(tokens[new_position]))
        return None, position

      self.configuration.report_parsing_debug("Stop DeclarationParser, found val declaration!",
          self.get_token_pos(tokens[position]))
      return ASTVal(val_token, ident_group, expression), new_position

    # Try to parse a 'fun-declaration'
    fun_token, new_position = self.get_next_string(tokens, position, "fun")
    if fun_token:
      ident_group, new_position = self.IdentGroupParser.parse(tokens, new_position)
      if not ident_group:
        self.configuration.report_parsing_error(
            "Found fun @%s but no identifier(s)!\n Instead '%s @ %s'" % \
                (str(self.get_token_pos(val_token)),
                 self.get_token_type_and_string(tokens[new_position]),
                 str(self.get_token_pos(tokens[new_position]))),
            self.get_token_pos(tokens[new_position]))
        return None, position

      ident_group, new_position = self.TypeParser.parse(tokens, new_position, ident_group)

      return_type_token = None
      colon_token, new_position = self.get_next_string(tokens, new_position, ":")
      if colon_token:
        return_type_token, new_position = self.get_next_type(tokens, new_position, "ident")

      equal_token, new_position = self.get_next_string(tokens, new_position, "=")
      if not equal_token:
        self.configuration.report_parsing_error(
            "Found fun @%s and identifier(s) but no '='!\n Instead '%s @ %s'" % \
                (str(self.get_token_pos(val_token)),
                 self.get_token_type_and_string(tokens[new_position]),
                 str(self.get_token_pos(tokens[new_position]))),
            self.get_token_pos(tokens[new_position]))
        return None, position

      expression, new_position = self.ExpressionParser.parse(tokens, new_position)
      if not expression:
        self.configuration.report_parsing_error(
            "Found val @%s, identifier(s) and '=' but no valid expression!\n Instead '%s @ %s'" % \
                (str(self.get_token_pos(val_token)),
                 self.get_token_type_and_string(tokens[new_position]),
                 str(self.get_token_pos(tokens[new_position]))),
            self.get_token_pos(tokens[new_position]))
        return None, position

      self.configuration.report_parsing_debug("Stop DeclarationParser, found fun declaration!",
          self.get_token_pos(tokens[position]))
      return ASTFun(val_token, ident_group, expression, return_type_token), new_position

    self.configuration.report_parsing_debug("Stop DeclarationParser, found nothing!",
        self.get_token_pos(tokens[position]))
    return None, position


class SMLToplevelParser(AbstractParser):

  def __init__(self, configuration):
    self.configuration = configuration
    self.DeclarationParser = SMLDeclarationParser(configuration)
    self.ExpressionParser  = SMLExpressionParser(configuration)

  def parse(self, tokens, position):
    self.configuration.report_parsing_debug("Start ToplevelParser!\n",
        self.get_token_pos(tokens[position]))

    declaration, new_position = self.DeclarationParser.parse(tokens, position)
    if declaration:
      self.configuration.report_parsing_debug("Stop ToplevelParser, found declaration!",
        self.get_token_pos(tokens[position]))
      return declaration, new_position

    if self.configuration.get_option('Parsing_Allow_Toplevel_Expressions', True):
      expression, new_position = self.ExpressionParser.parse(tokens, position)
      if expression:
        self.configuration.report_parsing_debug("Stop ToplevelParser, found expression!",
          self.get_token_pos(tokens[position]))
        return expression, new_position

    self.configuration.report_parsing_debug("Stop ToplevelParser, found nothing!",
      self.get_token_pos(tokens[position]))
    return None, position

class SMLParser(AbstractParser):

  def __init__(self, configuration):
    self.toplevelParser = SMLToplevelParser(configuration)
    self.toplevelNode   = ASTToplevelNode()
    self.configuration  = configuration

  def clear(self):
    print "CLEAR\n\n"
    self.toplevelNode.children = []
    print str(self.toplevelNode)

  def parse(self, tokens, position=0):
    print "DSASDADSADSA",tokens
    token_count = len(tokens)
    parsing_hit = True
    while position < token_count and parsing_hit:
      parsing_hit = False
      AST, position = self.toplevelParser.parse(tokens, position)
      if AST:
        parsing_hit = True
        self.toplevelNode.add_child(AST)
      elif not self.configuration.get_option('Parsing_Allow_Leftover_Tokens', False):
        self.configuration.report_parsing_error(
              "The following tokens could not be parsed:\n" \
            + " ".join(map(lambda x: x[1],tokens[position:])) + "\n\n" \
            + "Note: To allow leftover tokens set parse_as_much_as_possible = True")

    return (self.toplevelNode, position)


