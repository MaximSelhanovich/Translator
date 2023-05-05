from lexical_analyser import LexicalAnalyser
from token_data import *

if __name__ == '__main__':
    LexicalAnalyser('test.cpp').parse()
    TOKENS.print_table()
