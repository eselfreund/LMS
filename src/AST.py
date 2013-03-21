
#TODO Add configuration to all constructors !
class AbstractAST(object):

  def __init__(self, token = None, children = []):
    self.token         = token
    self.children      = children
    self.parent        = None
    self.explicit_typ  = None
    self.is_expression = False

  def add_child(self, child):
    self.children.append(child)
  
  def add_explicit_typ(self, typ):
    self.explicit_typ = typ
  
  def dump_ast(self, indent = 0):
    print " " * indent, self.__class__
    if self.token:
      print  " " * indent,self.token[0],":",self.token[1],"@(%i,%i)" % (self.token[2], self.token[3])
    for child in self.children:
      child.dump_ast(indent+4)
    print
  
  def validate(self, parent = None):
    self.parent = parent
    for child in self.children:
      child.validate(self)

  def traverse(self, func, pred_func = None, pred_recurse = None):
    if not pred_func or pred_func(self):
      func(self)
    if not pred_recurse or pred_recurse(self):
      for child in self.children:
        child.traverse(func, pred_func, pred_recurse)
  
  def get_token_text(self):
    return self.token[1] if self.token else ''

  def __str__(self):
    return self.to_string()

  def to_string(self):
    assert(0 and "Implement me!")
  

class ASTToplevelNode(AbstractAST):
  def __init__(self):
    super(ASTToplevelNode, self).__init__()
    print self.children

  def to_string(self):
    return "\n".join(map(lambda x: x.to_string(), self.children))

class ASTDeclaration(AbstractAST):
  def __init__(self, token = None, children = []):
    super(ASTDeclaration, self).__init__(token = token, children = children)
    
  def to_string(self):
    assert(0 and "This should be virtual")


class ASTVal(ASTDeclaration):
  def __init__(self, val_token, ident_group, expression):
    super(ASTVal, self).__init__(token = val_token, children = [ident_group, expression])

  def to_string(self):
    return "val " + self.children[0].to_string() + " = " + self.children[1].to_string()

class ASTFun(ASTDeclaration):
  def __init__(self, val_token, ident_group, expression, return_type_token = None):
    super(ASTFun, self).__init__(token = val_token, children = [ident_group, expression])
    self.return_type_token = return_type_token

  def to_string(self):
    s = "fun " + self.children[0].to_string()
    if self.return_type_token:
      s+= ":" + self.return_type_token[1]
    s += " = " + self.children[1].to_string()
    return s

class ASTExpression(AbstractAST):
  def __init__(self, token = None, children = []):
    super(ASTExpression, self).__init__(token = token, children = children)
    self.precedence = 0
    self.is_expression = True

  def to_string(self):
    assert(0 and "This should be virtual")


class ASTNumber(ASTExpression):

  def __init__(self, token):
    assert(token[0] == "number")
    super(ASTNumber, self).__init__(token = token)
    self.precedence = 100

  def to_string(self):
    return self.token[1] + ( " : " + self.explicit_typ.to_string() if self.explicit_typ else "")

  def __repr__(self):
    return "N %s" % self.token[1]

class ASTIdentifier(ASTExpression):

  def __init__(self, token):
    super(ASTIdentifier, self).__init__(token)
    self.precedence = 100

  def to_string(self):
    return self.token[1]+ ( " : " + self.explicit_typ.to_string() if self.explicit_typ else "")

  def __repr__(self):
    return str(self.token)

class ASTTuple(ASTExpression):

  def __init__(self, par_open_token, children, seperator = ","):
    super(ASTTuple, self).__init__(token = par_open_token, children = children)
    self.precedence = 100
    self.seperator  = seperator

  def to_string(self):
    if len(self.children) == 1:
      return self.children[0].to_string()
    return "(" + (self.seperator.join(map(lambda x: x.to_string(), self.children))) + ")" \
        + ( " : " + self.explicit_typ.to_string() if self.explicit_typ else "")

class ASTConditional(ASTExpression):

  def __init__(self, if_token, guard, consequence, alternative):
    super(ASTConditional, self).__init__(token = if_token, children = [guard, consequence, alternative])
    self.precedence = 100

  def to_string(self):
    s  = "if " + self.children[0].to_string()
    s += " then " + self.children[1].to_string()
    s += " else " + self.children[2].to_string()
    return s+ ( " : " + self.explicit_typ.to_string() if self.explicit_typ else "")

class ASTBinaryExpression(ASTExpression):

  def __init__(self, op_token, lhs, rhs):
    super(ASTBinaryExpression, self).__init__(token = op_token, children = [lhs, rhs])
    self.right_associativ = 0

  def to_string(self):
    s1 = self.children[0].to_string()
    s2 = self.children[1].to_string()
    if self.children[0].precedence < self.precedence and not self.right_associativ:
      s1 = "(" + s1 + ")"
    if self.children[1].precedence < self.precedence and self.right_assiocitiv:
      s2 = "(" + s2 + ")"
    return "("+s1 + self.token[1] + s2 +")" + ( " : " + self.explicit_typ.to_string() if self.explicit_typ else "")

class ASTDiv(ASTBinaryExpression):

  def __init__(self, div_token, lhs, rhs):
    super(ASTDiv, self).__init__(div_token, lhs, rhs)
    self.precedence = 3

class ASTMul(ASTBinaryExpression):

  def __init__(self, mul_token, lhs, rhs):
    super(ASTMul, self).__init__(mul_token, lhs, rhs)
    self.precedence = 3

class ASTPlus(ASTBinaryExpression):

  def __init__(self, plus_token, lhs, rhs):
    super(ASTPlus, self).__init__(plus_token, lhs, rhs)
    self.precedence = 2

class ASTMinus(ASTBinaryExpression):

  def __init__(self, minus_token, lhs, rhs):
    super(ASTMinus, self).__init__(minus_token, lhs, rhs)
    self.precedence = 2

class ASTEqual(ASTBinaryExpression):

  def __init__(self, equal_token, lhs, rhs):
    super(ASTEqual, self).__init__(equal_token, lhs, rhs)
    self.precedence = 1

class ASTNotEqual(ASTBinaryExpression):

  def __init__(self, not_equal_token, lhs, rhs):
    super(ASTNotEqual, self).__init__(not_equal_token, lhs, rhs)
    self.precedence = 1

class ASTLess(ASTBinaryExpression):

  def __init__(self, less_token, lhs, rhs):
    super(ASTLess, self).__init__(less_token, lhs, rhs)
    self.precedence = 1

class ASTGreater(ASTBinaryExpression):

  def __init__(self, greater_token, lhs, rhs):
    super(ASTGreater, self).__init__(greater_token, lhs, rhs)
    self.precedence = 1

class ASTApplication(ASTBinaryExpression):

  def __init__(self, lhs, rhs):
    super(ASTApplication, self).__init__(None, lhs, rhs)
    self.precedence = 4


