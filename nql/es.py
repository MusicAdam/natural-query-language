from .nql import NqlParser, EQ, LT, LTE, GT, GTE, NOT, NODE

QUERY = 'query'
AND = 'filter'
NOT_AND = 'must_not'
OR = 'should'
OPERATOR_QUERIES = {
  EQ: lambda key: 'term',
  GT: lambda key: 'gt'
}

class EsConverter(NqlParser):
  def __init__(self, type, verbose=False):
    super().__init__(verbose=verbose)
    self.type = type

  def convert(self, nql):
    self._context = _Context()
    self.parse(nql)
    return self._compile()
  
  def _compile(self):
    return '{' + self._context.operator.to_json() + '}'

  def predicate_not(self, node):
    self._context.toggle_not()

  def predicate_or(self, node):
    self._context.push(_Operator(OR, parent=self._context.operator))

    # ES Doesn't have should_not, its represented by should + must_not
    # TODO: Don't think this will work with not(or(1, 2, 3))
    if self._context.in_not:
      self._context.push(_Operator(NOT_AND, parent=self._context.operator))

  def predicate_and(self, node):
    if self._context.in_not:
      op_type = NOT_AND
    else:
      op_type = AND
    self._context.push(_Operator(op_type, parent=self._context.operator))
    
  def after(self, node):
    if node.data == NOT:
      self._context.toggle_not()
    
    if node.data != NODE:
      self._context.pop(node)

  def node(self, key, operator, value):
    # TODO: Based on mapping
    # TODO: Predicate factory building correct sub-classes
    self._context.push(_Predicate(key , value, OPERATOR_QUERIES[operator](key)))

class _Predicate:
  def __init__(self, key, value, query) -> None:
    self.key = key
    self.value = value
    self.query = query
  
  # TODO: to_json methods should just conver to dict 
  def to_json(self):
    return self.query + '\":{\"' + self.key + '\":\"' + self.value + '\"}'
    
class _Operator:
  def __init__(self, type, parent=None):
    self.type = type
    self.parent = parent
    self.children = []
  
  def add_child(self, child):
    self.children.append(child)

  def to_json(self):
    if len(self.children) == 1:
      op = self.children[0]
      return "\"" + op.type + "\"" + ":{" + op.to_json() + "}"
    else:
      arr = []
      for c in self.children:
        c_str = '{' + c.to_json() + '}'
        arr.append(c_str)
      return '[' + ','.join(arr) + ']'

class _QueryOperator(_Operator):
  def __init__(self, parent=None):
    super().__init__(QUERY, parent=parent)

  def to_json(self):
    return '"query":{"bool":{' + super().to_json() + "}}"
    
class _Context:
  def __init__(self) -> None:
    self.in_not = False
    self.operator = _QueryOperator()

  def toggle_not(self):
    self.in_not = not self.in_not
  
  def push(self, node):
    self.operator.add_child(node)

    if isinstance(node, _Operator):
      node.parent = self.operator
      self.operator = node
    
  def pop(self, node):
    self.operator = self.operator.parent