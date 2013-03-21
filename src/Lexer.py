import re

from Configuration import Configuration

class AbstractLexer(object):
  """
     Thanks to Eli Golovinsky for this piece of code.
     See http://www.gooli.org/blog/a-simple-lexer-in-python/
     for the originial source.
  """

  def __init__(self, definitions):
    self.definitions = definitions
    parts = []
    for name, part in definitions:
      parts.append("(?P<%s>%s)" % (name, part))
    self.regexpString = "|".join(parts)
    self.regexp = re.compile(self.regexpString, re.MULTILINE)

  def lex(self, text):
    """
       @Input Input string
       @Output Generator for tokens (type, value)
    """

    assert(type(text) == str)
    tokens = []
    pos_x  = 0
    pos_y  = 0
    # yield lexemes
    for match in self.regexp.finditer(text):
      found = False
      for name, rexp in self.definitions:
        m = match.group(name)
        if m is not None:
          if name != "space" and name != "newline":
            tokens.append((name, m, pos_x, pos_y))
          if m == "\n":
            pos_y += 1
            pos_x  = 0
          else:
            pos_x += len(m)
    return tokens


class SMLLexer(AbstractLexer):

  KEYWORDS  = ['val', 'fun', 'if', 'then', 'else']

  definitions = [
        # all keywords
        ("keyword"    , r"\b(%s)\b" % "|".join(KEYWORDS)),

        # operator
        ("operator"  , r"<>|[%s]" % re.escape('+-=*/(),:<>')),

        # legal identifiers
        ("ident"      , r"[A-Za-z_][A-Za-z0-9_']*"),

        # legal numbers (no support for hexadecimal and octal notations)
        ("number"     , r"[0-9.]+"),

        # free space of some kind
        ("space" , r"[\s\t]+"),
        ("newline" , r"\n"),

        # unrecognized patterns will be consumed by other
        ("other"      , r".+")
      ]

  def __init__(self, configuration):
    super(SMLLexer, self).__init__(SMLLexer.definitions)
    self.configuration = configuration



