from lark import Lark, Token
import os

text = """
NOT(
  OR(
    "contact.addresses[*].city"="Boston",
    AND(
      "contact.gifts[*].amount">"100",
      "contact.gifts[*].occurred_at">"2023-02-13"
    )
  )
)
"""
text2 = """
NOT(
  OR(
    AND(
      "contact.gifts[*].amount">"100",
      "contact.gifts[*].occurred_at">"2023-02-13"
    ),
    "contact.addresses[*].city"="Boston"
  )
)
"""

EQ = '='
LT = '<'
LTE = '<='
GT = '>'
GTE = '>='
NOT = 'not'
OR = 'fn_or'
AND = 'fn_and'
COMPARISON = 'comparison'

def repeat_to_length(string_to_expand, length):
  return (string_to_expand * (int(length/len(string_to_expand))+1))[:length]

class NqlParser:
  def __init__(self, verbose=False) -> None:
    self._depth = 0
    self._verbose = verbose

    with open(os.getcwd() + '/nql/nql.lark') as f:
      self.parser = Lark(f.read(), start='predicate')

  def parse(self, text):
    return self.parser.parse(text)
  
  #   self._execute(self._tree)

  # def _execute(self, tree):
  #   for node in tree.children:
  #     if isinstance(node, Token):
  #       return
  #     self._p(node.data)
  #     self._depth += 1

  #     do_after = False
  #     if node.data == NOT:
  #       self.predicate_not(node)
  #       do_after = True
  #     elif node.data == OR:
  #       self.predicate_or(node)
  #       do_after = True
  #     elif node.data == AND:
  #       self.predicate_and(node)
  #       do_after = True
  #     elif node.data == NODE:
  #       key = node.children[0].value
  #       operator = node.children[1].children[0].data.value 
  #       value = node.children[2].value
  #       self._p(f"{key}{operator}{value}", addtl_depth=1)
  #       self.node(
  #         key,
  #         operator,
  #         value,
  #       )
  #       do_after = True

  #     self._execute(node)
  #     if do_after:
  #       self.after(node)
  #     self._depth -= 1
  
  # def predicate_not(self, node):
  #   pass

  # def predicate_or(self, node):
  #   pass

  # def predicate_and(self, node):
  #   pass

  # def node(self, key, operator, value):
  #   pass

  # def after(self, node):
  #   pass

  # def _p(self, txt, addtl_depth=0):
  #   if not self._verbose:
  #     return
    
  #   tab=repeat_to_length('\t', self._depth + addtl_depth)
  #   print(tab + txt)