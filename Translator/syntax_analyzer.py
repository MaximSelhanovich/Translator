from token_data import *
from static_data import *
from treelib import Node, Tree

AST = Tree()


class SyntaxAnalyzer:
    def __init__(self):
        self.cur_parent = Node()
        self.cur_node = Node()

    def parse(self):
        for token in TOKENS:
            if token.value == '(':
                self.cur_parent = self.cur_node
                self.cur_node = Node()
            elif token.value in KEYWORDS_DEFINITION:
                for ident in IDENTIFIERS:
                    if ident.id == token.id + 1:
                        ident.data_type = token.value
            elif token.value in IDENTIFIERS:
                self.cur_node.data = token.value
                self.cur_node.set_predecessor(self.cur_parent)
