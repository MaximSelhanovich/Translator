from antlr4 import TokenStreamRewriter

from CustomCPP14ParserListener import CustomCPP14ParserListener
from lexical_analyser import LexicalAnalyser
from token_data import *
from lexical_errors import LexicalError
from CPP14Parser import CPP14Parser
from CPP14Lexer import CPP14Lexer
from CPP14ParserVisitor import CPP14ParserVisitor
from antlr4 import *
from parser_errors import *


def print_tree(tree, parser):
    #print(tree.toStringTree(parser))
    for i in range(tree.getChildCount()):
        if tree.getChildCount() == 0:
            continue
        child = tree.getChild(i)
        if isinstance(child, TerminalNode):
            print("  " + child.toString())
        else:
            print("  ", child)
            print_tree(child, parser)


class ASTNode:
    def __init__(self, name, children=None, value=None):
        self.name = name
        self.children = children or []
        self.value = value


def convert_tree_to_ast(tree):
    if tree is None:
        return None
    if isinstance(tree, TerminalNode):
        return ASTNode(tree.symbol.type, value=tree.symbol.text)
    else:
        children = [convert_tree_to_ast(child) for child in tree.children]
        return ASTNode(tree.getRuleContext().getText(), children=children)


def print_treex(node, level=0):
    print((' ' * level) + node.name, end='')
    if node.value is not None:
        print(f' ({node.value})', end='')
    print()
    for child in node.children:
        print_tree(child, level + 1)


data_types = ['char', 'int', 'short', 'long', 'long long', 'float', 'double', 'long double', 'bool', 'enum', 'void',
              'int&', 'int[]', 'struct', 'class', 'template', 'function', 'operator']


def print_tree(node, depth=0):
    visited = set()
    skip_depth = False
    indent = '  ' * depth
    if node.getChildCount() == 0:
        if node.getText() not in data_types:
            print(f"{indent}{node.getText()}")
    elif node not in visited:
        visited.add(node)
        for i in range(node.getChildCount()):
            if not skip_depth:
                print_tree(node.getChild(i), depth)
            else:
                print_tree(node.getChild(i), depth + 1)
            if i + 1 < node.getChildCount() and node.getChild(i + 1).getChildCount() > 0:
                skip_depth = True
            else:
                skip_depth = False


if __name__ == '__main__':
    try:
        input_stream = FileStream('test.cpp')
        lexer = CPP14Lexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = CPP14Parser(stream)
        listener = CustomCPP14ParserListener()
        parser.addParseListener(listener)
        tree = parser.translationUnit()
        print_tree(tree)
    except ParserError as ex:
        print(ex)

