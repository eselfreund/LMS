from Lexer import SMLLexer
from Parser import SMLParser
from Configuration import Configuration

configuration = Configuration()

lexer  = SMLLexer(configuration)
parser = SMLParser(configuration)

while 1:
  input_string = raw_input(">>")
  print "Input:",input_string

  tokens = lexer.lex(input_string)
  print "Tokens:", tokens

  AST, position  = parser.parse(tokens)
  if position != len(tokens):
    configuration.report_parsing_error("After parsing the following tokens were left:\n" \
        + " ".join(map(lambda x: x[1],tokens[position:])))

  if not AST:
    continue
  else:
    AST.dump_ast()
  print AST.to_string()
  parser.clear()

