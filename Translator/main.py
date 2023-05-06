from lexical_analyser import LexicalAnalyser
from token_data import *
from lexical_errors import LexicalError
from CPP14Parser import CPP14Parser
from CPP14Lexer import CPP14Lexer
from antlr4 import *
if __name__ == '__main__':
    input_stream = FileStream('test.cpp')
    lexer = CPP14Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CPP14Parser(stream)
    tree = parser.startRule()
