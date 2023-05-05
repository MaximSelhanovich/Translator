from dataclasses import dataclass
from typing import Any
from enum import Enum


@dataclass
class LiteralHelper:
    id: int
    data_type: Any


@dataclass
class IdentifierHelper(LiteralHelper):
    value: Any


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


class TokensTable(list):
    def print_table(self):
        print('*' * 41)
        print('{:>4}'.format('id'), '|', '{:>20}'.format('Token type'), '| Token value')
        print('*' * 41)
        for token in self.__iter__():
            print('{:>4}'.format(token.id), '|', '{:>20}'.format(token.type), '|', token.value)