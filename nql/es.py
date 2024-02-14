from .nql import NqlParser, EQ, LT, LTE, GT, GTE, NOT, COMPARISON
from .visitors import ExitingVistior
import json
import ast

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
    self._context.operator.add_child(COMPARISON_FACTORIES[operator](key, value), self._context)

  def fn_and(self, node):
    if self._context.in_not:
      op_type = NOT_AND
    else:
      op_type = AND
    self._context.push(_Operator(op_type))

  def fn_and_exit(self, node):
    self._context.pop(node)

  def fn_or(self, node):
    self._context.push(_Should())

  def fn_or_exit(self, node):
    self._context.pop(node)

  def fn_not(self, node):
    self._context.toggle_not()

class _Comparison:
  def __init__(self, key, value) -> None:
    self.key = key
    self.value = value

  def compile(self):
    pass
  
  # TODO: to_json methods should just conver to dict 
  def to_json(self):
    return self.query + '\":{\"' + self.key + '\":\"' + self.value + '\"}'

class _EQ(_Comparison):
  def compile(self):
    return {
      'term': {
        self.key: self.value
      }
    }

class _GT(_Comparison):
  def compile(self):
    return {
      'range': { 
        self.key: {
          'gt': self.value
        } 
      }
    }
  
COMPARISON_FACTORIES = {
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
  
class _Should(_Operator):
  def __init__(parent=None):
    super().__init__(OR, parent=parent)

  def add_child(self, child, context):
    if context.in_not:
      not_op = _Operator(NOT_AND)
      not_op.add_child(child, context)
      child = not_op
    super().add_child(child, context)


class _BoolQuery(_Operator):
  def __init__(self, parent=None):
    super().__init__(BOOL, parent=parent)

class _Query(_Operator):
  def __init__(self, parent=None):
    super().__init__(QUERY, parent=parent)
  
  def add_child(self, child, context):
    if len(self.children) == 1 and isinstance(self.children[0], _Comparison):
      new_child_root = _BoolQuery(parent=self)
      new_child_root.add_child(self.children[0], context)  
      self.children = [new_child_root]
    return super().add_child(child, context)
  
  def compile(self):
    if len(self.children) == 0:
      return {'query':{}}
    return {'query': self.children[0].compile()}

class _Context:
  def __init__(self) -> None:
    self.in_not = False
    self.operator = _Query()
  
  def compile(self):
    return self.operator.compile()

  def toggle_not(self):
    self.in_not = not self.in_not
  
  def push(self, node):
    if isinstance(node, _Operator):
      node.parent = self.operator
      self.operator.add_child(node, self)

      self.operator = node
    else:
      raise TypeError('can only push operators, use _Operator.add_child instead')

  def pop(self, tree):
    if not self.operator.parent:
      raise ValueError('root operator cannot be popped')
    
    self.operator = self.operator.parent