from dataclasses import dataclass
from typing import Any
@dataclass
class Token:
    id: int
    type: Any
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
    'return'
}


OPERATORS = {
    '+',
    '-',
    '*',
    '/',
    '=',
    '+=',
    '-=',
    '*=',
    '/=',
    '==',
    '|',
    '&',
    '||',
    '&&'
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


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
