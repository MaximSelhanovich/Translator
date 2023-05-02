from dataclasses import dataclass
from typing import Any
from enum import Enum, Flag, auto


class TokenType(Enum):
    LITERAL = 'literal'
    COMMENT = 'comment'
    IDENTIFIER = 'identifier'
    SEPARATOR = 'separator'
    OPERATOR = 'operator'
    KEY_WORD = 'key_word'


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
        message = f"Unknown token at ({line}, {column}) with value ({token_value})"
        self.message = message
        super().__init__(self.message)


KEY_WORDS = {
    'void',
    'string',
    'int',
    'double',
    'bool',
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
    ':'
    ','
}

LITERALS = {}
COMMENTS = {}
IDENTIFIERS = {}


class STATES(Flag):
    NOTHING = auto()
    STRING = auto()
    SLASH = auto()
    NUMBER = auto()
    DOT = auto()
    OPERATOR = auto()


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
        print(f"id: {self.cur_token.id}, type: {self.cur_token.type.value}, value: {self.cur_token.value}")
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
        self.CURRENT_STATE = STATES.NUMBER
        self.cur_col_index += 1
        while self.cur_col_index < len(self.cur_line):
            ch = self.cur_line[self.cur_col_index]
            if ch == '.':
                if STATES.DOT in self.CURRENT_STATE:
                    self.cur_token.value += ch
                    raise UnknownTokenError(self.cur_line_index, self.cur_col_index, self.cur_token.value)
                self.CURRENT_STATE |= STATES.DOT
            elif not ch.isdigit():
                self.cur_col_index -= 1
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

    def parse(self):
        while self.cur_line_index < len(self.lines):
            self.cur_line = self.lines[self.cur_line_index].strip()
            self.cur_col_index = 0
            while self.cur_col_index < len(self.cur_line):
                cur_char = self.cur_line[self.cur_col_index]
                if cur_char.isspace() and self.cur_token.value is not None:
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
                self.cur_col_index += 1
            self.cur_line_index += 1


if __name__ == '__main__':
    LexicalAnalyser('test.cpp').parse()
