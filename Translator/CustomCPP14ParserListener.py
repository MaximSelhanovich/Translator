from CPP14ParserListener import CPP14ParserListener
from CPP14Parser import CPP14Parser
from parser_errors import *
from dataclasses import dataclass
from typing import Any
from static_data import *

@dataclass
class Identifier:
    name: str
    type: Any
    nesting_level: int
    nesting_block: int
    value: Any


class IdentifierTable(list):
    def check_identifier(self, var_name: str, nesting_block: int, nesting_level: int):
        if nesting_level < -1:
            return False
        for i in self.__iter__():
            if i.name == var_name and i.nesting_block == nesting_block and i.nesting_level == nesting_level:
                return True
        return self.check_identifier(var_name, nesting_block, nesting_level - 1)

    def get_identifier(self, var_name: str, nesting_block: int, nesting_level: int):
        if nesting_level < -1:
            return None
        for i in self.__iter__():
            if i.name == var_name and i.nesting_block == nesting_block and i.nesting_level == nesting_level:
                return i
        return self.get_identifier(var_name, nesting_block, nesting_level - 1)

    def add_token(self, token):
        self.append(token)


class CustomCPP14ParserListener(CPP14ParserListener):
    def __init__(self):
        self.in_cycle = False
        self.vars = IdentifierTable()
        # +1 on entering function makes nesting_level = 0
        self.nesting_level = -1
        self.nesting_block = -1
        self.identifier = Identifier(None, None, None, None, None)
        self.class_creation = False;
        self.cls = ['string']
        self.cur_id = None
        self.in_declarator = False
        self.translate_type_str_to_num = {
            'int': CPP14Parser.IntegerLiteral,
            'char': CPP14Parser.CharacterLiteral,
            'float': CPP14Parser.FloatingLiteral,
            'double': CPP14Parser.FloatingLiteral,
            'string': CPP14Parser.StringLiteral,
            'bool': CPP14Parser.BooleanLiteral,
            'pointer': CPP14Parser.PointerLiteral
        }

        self.translate_type_num_to_str = {
            CPP14Parser.IntegerLiteral: 'int',
            CPP14Parser.CharacterLiteral: 'char',
            CPP14Parser.FloatingLiteral: 'float',
            CPP14Parser.StringLiteral: 'string',
            CPP14Parser.BooleanLiteral: 'bool',
            CPP14Parser.PointerLiteral: 'pointer'
        }

    def get_line_column(self, ctx):
        start, end = ctx.getSourceInterval()
        tokens = ctx.parser.getInputStream().tokens[start:end+1]
        start_token = tokens[0]
        end_token = tokens[-1]
        start_line = start_token.line
        start_column = start_token.column
        end_line = end_token.line
        end_column = end_token.column + len(end_token.text) - 1
        return start_line, start_column + 1

    def enterIterationStatement(self, ctx:CPP14Parser.IterationStatementContext):
        self.in_cycle = True
        pass

    def exitIterationStatement(self, ctx:CPP14Parser.IterationStatementContext):
        self.in_cycle = False
        pass

    def enterJumpStatement(self, ctx:CPP14Parser.JumpStatementContext):
        pass

    def exitJumpStatement(self, ctx:CPP14Parser.JumpStatementContext):
        if not self.in_cycle and (ctx.Break() is not None or ctx.Continue() is not None):
            msg = 'break' if ctx.Break() is not None else 'continue'
            (line, col) = self.get_line_column(ctx)
            raise JumpStatementError(line, col, msg + ' statement out of loop')

    def enterSimpleTypeSpecifier(self, ctx:CPP14Parser.SimpleTypeSpecifierContext):
        #print(ctx.Int(), 'enter')
        pass

    def exitSimpleTypeSpecifier(self, ctx:CPP14Parser.SimpleTypeSpecifierContext):
        self.identifier.type = ctx.getText()
        self.identifier.nesting_block, self.identifier.nesting_level = self.nesting_block, self.nesting_level

    def enterUnqualifiedId(self, ctx:CPP14Parser.UnqualifiedIdContext):
        pass

    def exitUnqualifiedId(self, ctx:CPP14Parser.UnqualifiedIdContext):
        if not self.in_declarator and not self.vars.check_identifier(ctx.getText(), self.nesting_block, self.nesting_level):
            if ctx.getText() in KEYWORDS:
                return
            lin, col = self.get_line_column(ctx)
            raise UnknownIdentifier(lin, col, f'unknown identifier ({ctx.getText()})')

    def enterFunctionDefinition(self, ctx:CPP14Parser.FunctionDefinitionContext):
        self.nesting_block += 1
        pass

    def exitFunctionDefinition(self, ctx:CPP14Parser.FunctionDefinitionContext):
        pass

    def enterCompoundStatement(self, ctx:CPP14Parser.CompoundStatementContext):
        self.nesting_level += 1

    def exitCompoundStatement(self, ctx:CPP14Parser.CompoundStatementContext):
        self.nesting_level -= 1

    def enterClassName(self, ctx:CPP14Parser.ClassNameContext):
        pass

    # Exit a parse tree produced by CPP14Parser#className.
    def exitClassName(self, ctx:CPP14Parser.ClassNameContext):
        if not self.class_creation and ctx.getText() not in self.cls:
            lin, col = self.get_line_column(ctx)
            raise UnknownIdentifier(lin, col, f'unknown identifier ({ctx.getText()})')

    def enterBraceOrEqualInitializer(self, ctx:CPP14Parser.BraceOrEqualInitializerContext):
        pass

    def exitBraceOrEqualInitializer(self, ctx:CPP14Parser.BraceOrEqualInitializerContext):
        l_token_type = self.translate_type_str_to_num[self.cur_id.type]
        r_token_type = self.get_token_type(ctx.getChild(1).start)
        if l_token_type != r_token_type:
            lin, col = self.get_line_column(ctx)
            raise TypeMissmatch(lin, col, f'Type missmatch with ({self.translate_type_num_to_str[l_token_type]}) '
                                          f'and ({self.translate_type_num_to_str[r_token_type]})')
        self.cur_id.value = ctx.getChild(1).getText()
        pass

    def enterDeclarator(self, ctx:CPP14Parser.DeclaratorContext):
        self.in_declarator = True
        pass

    def exitDeclarator(self, ctx:CPP14Parser.DeclaratorContext):
        self.in_declarator = False
        lin, col = self.get_line_column(ctx)
        ctx = ctx.getChild(0)
        if self.identifier.type is None:
            if not self.vars.check_identifier(ctx.getText(), self.nesting_block, self.nesting_level):
                if not ctx.getText() in KEYWORDS:
                    raise UnknownIdentifier(lin, col, f'unknown identifier ({ctx.getText()})')
            self.cur_id = self.vars.get_identifier(ctx.getText(), self.nesting_block, self.nesting_level)
        else:
            if self.vars.check_identifier(ctx.getText(), self.nesting_block, self.nesting_level):
                raise DoubleDeclaration(lin, col, f'double identifier declaration ({ctx.getText()})')
            self.identifier.name = ctx.getText()
            self.vars.add_token(self.identifier)
            self.cur_id = self.identifier
            self.identifier = Identifier(None, None, None, None, None)

    def enterInitializer(self, ctx:CPP14Parser.InitializerContext):
        #self.in_declarator = True
        pass
    def exitInitializer(self, ctx:CPP14Parser.InitializerContext):
        # self.in_declarator = False
        pass

    def enterMultiplicativeExpression(self, ctx:CPP14Parser.MultiplicativeExpressionContext):
        pass

    def exitMultiplicativeExpression(self, ctx:CPP14Parser.MultiplicativeExpressionContext):
        if len(ctx.Div()) != 0 and ctx.getChild(2).getText() == '0':
                lin, col = self.get_line_column(ctx)
                raise ZeroDivision(lin, col, 'division by zero')

    def enterEqualityExpression(self, ctx:CPP14Parser.EqualityExpressionContext):
        pass

    def get_token_type(self, token):
        token_type = token.type
        if token_type == CPP14Parser.Identifier:
            token_type = self.translate_type_str_to_num[self.vars.get_identifier(token.text, self.nesting_block, self.nesting_level).type]
        return token_type

    def exitEqualityExpression(self, ctx:CPP14Parser.EqualityExpressionContext):
        if ctx.getChildCount() == 3:
            l_token_type = self.get_token_type(ctx.getChild(0).start)
            r_token_type = self.get_token_type(ctx.getChild(2).start)
            if l_token_type != r_token_type:
                lin, col = self.get_line_column(ctx)
                raise TypeMissmatch(lin, col, f'Type missmatch with ({self.translate_type_num_to_str[l_token_type]}) '
                                              f'and ({self.translate_type_num_to_str[r_token_type]})')
        pass
