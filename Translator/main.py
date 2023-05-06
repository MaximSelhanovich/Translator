from lexical_analyser import LexicalAnalyser
from token_data import *
from lexical_errors import LexicalError

if __name__ == '__main__':
    try:
        LexicalAnalyser('test.cpp').parse()
        TOKENS.print_unique(TokenType.IDENTIFIER)
        TOKENS.print_unique(TokenType.KEYWORD)
        TOKENS.print_unique(TokenType.OPERATOR)
        TOKENS.print_unique(TokenType.LITERAL)
    except LexicalError as err:
        print(err)
