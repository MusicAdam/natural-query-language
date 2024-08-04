from .nql import NqlParser, EQ, LT, LTE, GT, GTE, NOT, COMPARISON
from .visitors import ExitingVistior
import json
import ast
from abc import ABC

BOOL = 'bool'
QUERY = 'query'
AND = 'filter'
NOT_AND = 'must_not'
OR = 'should'

# TODO: Use transformer to combine gt etc.?

class EsTransformer:
  def to_json(self, tree, pretty=False):
    indent = 2 if pretty else None
    return json.dumps(self.to_dict(tree), indent=indent)
  
  def to_dict(self, tree):
    builder = EsDictBuilder()
    return builder.transform(tree)

class EsDictBuilder(ExitingVistior):
  """
  EsDictBuilder traverses the NQL AST Tree, building the ES query long the way.
  """
  def transform(self, tree) -> dict:
    self._context = _Context()
    self.visit_topdown(tree)
    return self._context.compile()

  def comparison(self, node):
    # TODO: Is literal eval secure?
    key = ast.literal_eval(node.children[0].value)
    operator = node.children[1].children[0].value 
    value = ast.literal_eval(node.children[2].value)
    # TODO: Based on mapping
    # TODO: Predicate factory building correct sub-classes
    self._context.operator.add_child(COMPARATOR_FACTORIES[operator](key, value), self._context)

  def fn_and(self, node):
    if self._context.in_not:
      op = _MustNot()
    else:
      op = _Must()
    self._context.push(op)

  def fn_and_exit(self, node):
    self._context.pop(node)

  def fn_or(self, node):
    self._context.push(_Should())

  def fn_or_exit(self, node):
    self._context.pop(node)

  def fn_not(self, node):
    self._context.toggle_not()

class _Comparator(ABC):
  def __init__(self, key, value) -> None:
    self.key = key
    self.value = value

  def compile(self):
    pass

class _EQ(_Comparator):
  def compile(self):
    return {
      'term': {
        self.key: self.value
      }
    }

class _GT(_Comparator):
  def compile(self):
    return {
      'range': { 
        self.key: {
          'gt': self.value
        } 
      }
    }
  
COMPARATOR_FACTORIES = {
  EQ: _EQ,
  GT: _GT
}


class _Operator:
  def __init__(self, type, parent=None):
    self.type = type 
    self.parent = parent
    self.children = []
  
  def add_child(self, child, context):
    child.parent = self
    self.children.append(child)

  def compile(self):
    q = {}
    if len(self.children) == 1:
      q[self.type] = self.children[0].compile()
    else:
      compiled_children = []
      for child in self.children:
        compiled_children.append(child.compile())
      q[self.type] = compiled_children
    return q
  
  def pop(self, context):
    pass
  
class _Should(_Operator):
  def __init__(parent=None):
    super().__init__(OR, parent=parent)

  def add_child(self, child, context):
    if context.in_not:
      not_op =_MustNot
      not_op.add_child(child, context)
      child = not_op
    super().add_child(child, context)

class _Must(_Operator):
  def __init__(self, parent=None):
    super().__init__(AND, parent)

class _MustNot(_Operator):
  def __init__(self, parent=None):
    super().__init__(NOT_AND, parent)

class _BoolQuery(_Operator):
  def __init__(self, parent=None):
    super().__init__(BOOL, parent=parent)
  
  # def compile(self):
  #   if len(self.children) == 1 and isinstance(self.children[0], _Comparator):
  #     return { self.type: { AND: self.children[0].compile() } }
  #   return super().compile()

class _Query(_Operator):
  def __init__(self, parent=None):
    super().__init__(QUERY, parent=parent)

  def add_child(self, child, context):
    # Operators all go under a bool query, so account for that
    if isinstance(child, _Operator):
      bool_query = _BoolQuery()
      bool_query.add_child(child, context)
      context.push(bool_query, add_child=False)
      self.children.append(bool_query)
    else:
      super().add_child(child, context=context)
  
  def compile(self):
    if len(self.children) == 0:
      return {'query':{}}
    return super().compile()

class _Context:
  def __init__(self) -> None:
    self.in_not = False
    self.operator = _Query()
    self._pop_ct = 0
  
  def compile(self):
    return self.operator.compile()

  def toggle_not(self):
    self.in_not = not self.in_not

  def insert_above_operator
  
  def push(self, node, add_child=True):
    if isinstance(node, _Operator):
      node.parent = self.operator

      if add_child:
        self.operator.add_child(node, self)

      self.operator = node
      self._pop_ct += 1
    else:
      raise TypeError('can only push operators, use _Operator.add_child instead')

  def pop(self, node):
    """
    Since operators can add nodes, pop until we get to the expected node
    """
    while self._pop_ct > 0:
      if not self.operator.parent:
        raise ValueError('root operator cannot be popped')
      
      if isinstance(self.operator, _Operator):
        self.operator.pop(self)
      self.operator = self.operator.parent

      self._pop_ct -= 1