from enum import Flag, auto
from lexical_errors import *
from static_data import *
from token_data import *


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

    def check_identifier_existence(self):
        for i in IDENTIFIERS:
            if TOKENS[i.id].value == self.cur_token.value:
                return True
        return False

    def add_token(self):
        self.cur_token.id = self.cur_token_id
        TOKENS.append(self.cur_token)
        if self.cur_token.type == TokenType.LITERAL:
            LITERALS.append(LiteralHelper(self.cur_token.id, self.CURRENT_STATE))
        elif self.cur_token.type == TokenType.IDENTIFIER:
            if STATES.DEFINITION in self.CURRENT_STATE:
                if self.check_identifier_existence():
                    raise DoubleDeclarationError(self.cur_line_index, self.cur_col_index, self.cur_token.value)
                IDENTIFIERS.append(IdentifierHelper(self.cur_token.id, None, None))
                self.CURRENT_STATE ^= STATES.DEFINITION
            elif not self.check_identifier_existence():
                raise UnknownTokenError(self.cur_line_index, self.cur_col_index, self.cur_token.value,
                                        ' unknown identifier')
        self.cur_token = Token(None, None, None)
        self.CURRENT_STATE |= STATES.NOTHING
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
                if ch not in ['t', 'r', 'n', '"', '\\']:
                    raise UnknownTokenError(self.cur_line_index, self.cur_col_index, self.cur_token.value,
                                            ' unknown escape sequence')
                self.CURRENT_STATE ^= STATES.SLASH
            elif ch == '"' and STATES.SLASH not in self.CURRENT_STATE:
                self.add_token()
                return
            elif self.cur_col_index == len(self.cur_line) - 1:
                raise UnknownTokenError(self.cur_line_index, self.cur_col_index, self.cur_token.value,
                                        ' missing " character')
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
                    raise UnknownTokenError(self.cur_line_index, self.cur_col_index, self.cur_token.value,
                                            ' wrong number of dots for double')
                self.CURRENT_STATE = STATES.DOUBLE
            elif not ch.isdigit():
                self.cur_col_index -= 1
                if ch.isalpha():
                    self.cur_token.value += ch
                    raise UnknownTokenError(self.cur_line_index, self.cur_col_index, self.cur_token.value,
                                            ' wrong character for number')
                self.add_token()
                return
            self.cur_col_index += 1
            self.cur_token.value += ch

    def parse_operator(self):
        cur_char = self.cur_line[self.cur_col_index]
        if self.CURRENT_STATE == STATES.OPERATOR:
            self.cur_token.value += cur_char
            if self.cur_token.value not in TWO_CHAR_OPERATORS:
                raise UnknownTokenError(self.cur_line_index, self.cur_col_index, self.cur_token.value,
                                        'unknown operator')
            self.add_token()
            return
        self.CURRENT_STATE = STATES.OPERATOR
        self.cur_token.value = cur_char
        self.cur_token.type = TokenType.OPERATOR

    def parse_non_literal(self):
        # self.CURRENT_STATE = STATES.STRING
        self.cur_token.type = TokenType.IDENTIFIER
        self.cur_token.value = self.cur_line[self.cur_col_index]
        self.cur_col_index += 1
        while self.cur_col_index < len(self.cur_line):
            ch = self.cur_line[self.cur_col_index]
            if not ch.isalpha() and ch != '_':
                if self.cur_token.value == 'true' or self.cur_token.value == 'false':
                    self.CURRENT_STATE = STATES.BOOL
                    self.cur_token.type = TokenType.LITERAL
                elif self.cur_token.value in KEYWORDS_DEFINITION.union(KEYWORDS):
                    if self.cur_token.value in KEYWORDS_DEFINITION:
                        self.CURRENT_STATE = STATES.DEFINITION
                    self.cur_token.type = TokenType.KEYWORD
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
                    raise UnknownTokenError(self.cur_line_index, self.cur_col_index, cur_char,
                                            ' unknown character')
                self.cur_col_index += 1
            self.cur_line_index += 1
