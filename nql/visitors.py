from lark import Tree
from lark.visitors import Visitor_Recursive

"""
ExitingVisitor extend's VisitorRecursive's base functionality to expose *_exit methods which allow 
implementing classes to know when a node is left 
"""
class ExitingVistior(Visitor_Recursive):
  def _call_exit_userfunc(self, tree):
      return getattr(self, tree.data + "_exit", self.__default__)(tree)
    
  def visit_topdown(self, tree: Tree) -> Tree:
    out = super().visit_topdown(tree)
    self._call_exit_userfunc(out)
    return out
  
  def visit(self, tree: Tree) -> Tree:
    out = super().visit(tree)
    self._call_exit_userfunc(out)
    return out