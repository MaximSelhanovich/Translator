from dataclasses import dataclass
from typing import Any
from enum import Enum, Flag, auto


class TokenType(Enum):
    LITERAL = 'literal'
    COMMENT = 'comment'
    IDENTIFIER = 'identifier'
    SEPARATOR = 'separator'
    OPERATOR = 'operator'
    KEYWORD = 'keyword'


@dataclass
class Token:
    id: int
    type: TokenType
    value: Any


class UnknownTokenError(Exception):
    def __init__(self, line, column, token_value):
        self.line = line
        self.column = column
        self.token_value = token_value
        message = f'Unknown token at ({line}, {column}) with value ({token_value})'
        self.message = message
        super().__init__(self.message)


TOKENS = []


KEYWORDS_DEFINITION = {
    'void',
    'string',
    'int',
    'double',
    'bool'
}


KEYWORDS = {
    'true',
    'false',
    'if',
    'else',
    'while',
    'do',
    'for',
    'continue',
    'break',
    'return',
    'cin',
    'cout'
}


ONE_CHAR_OPERATORS = {
    '+',
    '-',
    '*',
    '/',
    '=',
    '<',
    '>',
    '|',
    '&',
}

TWO_CHAR_OPERATORS = {
    '++',
    '--',
    '<<',
    '>>',
    '+=',
    '-=',
    '*=',
    '/=',
    '==',
    '||',
    '&&',
    '>=',
    '<='
}

SEPARATORS = {
    '{',
    '}',
    '[',
    ']',
    '(',
    ')',
    ';',
    ':',
    ','
}


@dataclass
class LiteralHelper:
    id: int
    data_type: Any


@dataclass
class IdentifierHelper(LiteralHelper):
    value: Any

LITERALS = []
COMMENTS = {}
IDENTIFIERS = []


class STATES(Flag):
    NOTHING = auto()
    STRING = auto()
    SLASH = auto()
    INT = auto()
    DOUBLE = auto()
    BOOL = auto()
    DOT = auto()
    OPERATOR = auto()
    DEFINITION = auto()


class LexicalAnalyser:
    def __init__(self, file_name):
        self.file_name = file_name
        with open(file_name) as f:
            self.lines = f.readlines()
        self.CURRENT_STATE: STATES = STATES.NOTHING
        self.cur_line_index: int = 0
        self.cur_col_index: int = 0
        self.cur_token: Token = Token(0, TokenType.COMMENT, None)
        self.cur_line = None
        self.cur_token_id: int = 0

    def add_token(self):
        self.cur_token.id = self.cur_token_id
        TOKENS.append(self.cur_token)
        if self.cur_token.type == TokenType.LITERAL:
            LITERALS.append(LiteralHelper(self.cur_token.id, self.CURRENT_STATE))
        # elif self.cur_token.type == TokenType.IDENTIFIER:
          #  IDENTIFIERS.append()
        print(f"id: {self.cur_token.id}, type: {self.cur_token.type}, value: {self.cur_token.value}")
        self.cur_token = Token(None, None, None)
        self.CURRENT_STATE = STATES.NOTHING
        self.cur_token_id += 1

    def parse_string_literal(self):
        self.CURRENT_STATE = STATES.STRING
        self.cur_token.type = TokenType.LITERAL

        self.cur_token.value = self.cur_line[self.cur_col_index]
        self.cur_col_index += 1
        while self.cur_col_index < len(self.cur_line):
            ch = self.cur_line[self.cur_col_index]
            self.cur_token.value += ch
            if ch == '\\':
                self.CURRENT_STATE |= STATES.SLASH
            elif STATES.SLASH in self.CURRENT_STATE:
                self.CURRENT_STATE ^= STATES.SLASH
            elif ch == '"' and STATES.SLASH not in self.CURRENT_STATE:
                self.add_token()
                return
            self.cur_col_index += 1

    def parse_number_literal(self):
        self.cur_token.type = TokenType.LITERAL
        if self.CURRENT_STATE == STATES.OPERATOR:
            self.cur_token.value += self.cur_line[self.cur_col_index]
        else:
            self.cur_token.value = self.cur_line[self.cur_col_index]
        self.CURRENT_STATE = STATES.INT
        self.cur_col_index += 1
        while self.cur_col_index < len(self.cur_line):
            ch: str = self.cur_line[self.cur_col_index]
            if ch == '.':
                if self.CURRENT_STATE == STATES.DOUBLE:
                    self.cur_token.value += ch
                    raise UnknownTokenError(self.cur_line_index, self.cur_col_index, self.cur_token.value)
                self.CURRENT_STATE = STATES.DOUBLE
            elif not ch.isdigit():
                self.cur_col_index -= 1
                if ch.isalpha():
                    self.cur_token.value += ch
                    raise UnknownTokenError(self.cur_line_index, self.cur_col_index, self.cur_token.value)
                self.add_token()
                return
            self.cur_col_index += 1
            self.cur_token.value += ch

    def parse_operator(self):
        cur_char = self.cur_line[self.cur_col_index]
        if self.CURRENT_STATE == STATES.OPERATOR:
            self.cur_token.value += cur_char
            if self.cur_token.value not in TWO_CHAR_OPERATORS:
                raise UnknownTokenError(self.cur_line_index, self.cur_col_index, self.cur_token.value)
            self.add_token()
            return
        self.CURRENT_STATE = STATES.OPERATOR
        self.cur_token.value = cur_char
        self.cur_token.type = TokenType.OPERATOR

    def parse_non_literal(self):
        # self.CURRENT_STATE = STATES.STRING
        # self.cur_token.type = TokenType.LITERAL

        self.cur_token.value = self.cur_line[self.cur_col_index]
        self.cur_col_index += 1
        while self.cur_col_index < len(self.cur_line):
            ch = self.cur_line[self.cur_col_index]
            if not ch.isalpha() and ch != '_':
                if self.cur_token.value == 'true' or self.cur_token.value == 'false':
                    self.CURRENT_STATE = STATES.BOOL
                    self.cur_token.type = TokenType.LITERAL
                elif self.cur_token.value in KEYWORDS_DEFINITION or self.cur_token.value in KEYWORDS:
                    self.CURRENT_STATE = STATES.DEFINITION
                    self.cur_token.type = TokenType.KEYWORD
                else:
                    self.cur_token.type = TokenType.IDENTIFIER
                self.add_token()
                self.cur_col_index -= 1
                return
            self.cur_token.value += ch
            self.cur_col_index += 1

    def parse(self):
        while self.cur_line_index < len(self.lines):
            self.cur_line = self.lines[self.cur_line_index].strip()
            self.cur_col_index = 0
            while self.cur_col_index < len(self.cur_line):
                cur_char = self.cur_line[self.cur_col_index]
                if cur_char.isspace():
                    if self.cur_token.value is not None:
                        self.add_token()
                elif cur_char in SEPARATORS:
                    self.cur_token.value = cur_char
                    self.cur_token.type = TokenType.SEPARATOR
                    self.add_token()
                elif cur_char in ONE_CHAR_OPERATORS:
                    self.parse_operator()
                elif cur_char == '"':
                    self.parse_string_literal()
                elif cur_char.isdigit():
                    self.parse_number_literal()
                elif cur_char.isalpha() or cur_char == '_':
                    self.parse_non_literal()
                else:
                    raise UnknownTokenError(self.cur_line_index, self.cur_col_index, cur_char)
                self.cur_col_index += 1
            self.cur_line_index += 1


if __name__ == '__main__':
    print(STATES.BOOL)
    LexicalAnalyser('test.cpp').parse()
