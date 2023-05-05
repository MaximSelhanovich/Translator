class LexicalError(Exception):
    def __init__(self, line, column, message):
        self.line = line
        self.column = column
        self.message = message
        super().__init__(self.message)


class UnknownTokenError(LexicalError):
    def __init__(self, line, column, token_value, add_msg=None):
        self.token_value = token_value
        self.message = f'Error at ({line}, {column}) with value ({token_value})' + add_msg
        super().__init__(line, column, self.message)


class DoubleDeclarationError(LexicalError):
    def __init__(self, line, column, token_value):
        self.token_value = token_value
        self.message = f'Error at ({line}, {column}): double declaration with value ({token_value})'
        super().__init__(line, column, self.message)
