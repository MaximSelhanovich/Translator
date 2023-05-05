from lexical_analyser import LexicalAnalyser
from syntax_analyzer import SyntaxAnalyzer
from token_data import *
from lexical_errors import LexicalError

if __name__ == '__main__':
    try:
        LexicalAnalyser('test.cpp').parse()
        TOKENS.print_table()
    except LexicalError as err:
        print(err)