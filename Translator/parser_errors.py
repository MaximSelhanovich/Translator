

class ParserError(Exception):
    def __init__(self, line, column, message):
        self.line = line
        self.column = column
        self.message = message + f' at ({line}, {column})'
        super().__init__(self.message)


class JumpStatementError(ParserError):
    def __init__(self, line, column, message):
        super().__init__(line, column, message)


class UnknownIdentifier(ParserError):
    def __init__(self, line, column, message):
        super().__init__(line, column, message)


class DoubleDeclaration(ParserError):
    def __init__(self, line, column, message):
        super().__init__(line, column, message)


class ZeroDivision(ParserError):
    def __init__(self, line, column, message):
        super().__init__(line, column, message)


class TypeMissmatch(ParserError):
    def __init__(self, line, column, message):
        super().__init__(line, column, message)