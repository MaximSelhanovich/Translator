from CPP14ParserListener import CPP14ParserListener
from CPP14Parser import CPP14Parser
from parser_errors import *
from dataclasses import dataclass
from typing import Any


@dataclass
class Identifier:
    name: str
    type: Any
    nesting_level: int
    nesting_block: int
    value: Any


class IdentifierTable(list):
    def check_variable(self, var_name: str, nesting_block: int, nesting_level: int):
        if nesting_level < -1:
            return False
        for i in self.__iter__():
            if i.name == var_name and i.nesting_block == nesting_block and i.nesting_level == nesting_level:
                return True
        return self.check_variable(var_name, nesting_block, nesting_level - 1)

    def add_token(self, token):
        self.append(token)


class CustomCPP14ParserListener(CPP14ParserListener):
    def __init__(self):
        self.in_cycle = False
        self.vars = IdentifierTable()
        # +1 on entering function makes nesting_level = 0
        self.nesting_level = -1
        self.nesting_block = 0
        self.identifier = Identifier(None, None, None, None, None)
        self.class_creation = False;
        self.cls = []

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
        print('first')
        pass

    def enterUnqualifiedId(self, ctx:CPP14Parser.UnqualifiedIdContext):
        pass

    def exitUnqualifiedId(self, ctx:CPP14Parser.UnqualifiedIdContext):
        lin, col = self.get_line_column(ctx)
        if self.identifier.type is None:
            if not self.vars.check_variable(ctx.getText(), self.nesting_block, self.nesting_level):
                raise UnknownIdentifier(lin, col, f'unknown identifier ({ctx.getText()})')
        else:
            if self.vars.check_variable(ctx.getText(), self.nesting_block, self.nesting_level):
                raise DoubleDeclaration(lin, col, f'double identifier declaration ({ctx.getText()})')
            self.identifier.name = ctx.getText()
            self.vars.add_token(self.identifier)
            self.identifier = Identifier(None, None, None, None, None)

    def enterFunctionDefinition(self, ctx:CPP14Parser.FunctionDefinitionContext):
        self.nesting_block += 1
        pass

    def exitFunctionDefinition(self, ctx:CPP14Parser.FunctionDefinitionContext):
        pass

    def enterCompoundStatement(self, ctx:CPP14Parser.CompoundStatementContext):
        self.nesting_level += 1

    def exitCompoundStatement(self, ctx:CPP14Parser.CompoundStatementContext):
        self.nesting_level -= 1

    def enterDeclSpecifierSeq(self, ctx:CPP14Parser.DeclSpecifierSeqContext):
        pass

    # Exit a parse tree produced by CPP14Parser#declSpecifierSeq.
    def exitDeclSpecifierSeq(self, ctx:CPP14Parser.DeclSpecifierSeqContext):
        print(ctx.getText(), ' in declSpec')
        pass

    def enterSimpleDeclaration(self, ctx:CPP14Parser.SimpleDeclarationContext):
        pass

    # Exit a parse tree produced by CPP14Parser#simpleDeclaration.
    def exitSimpleDeclaration(self, ctx:CPP14Parser.SimpleDeclarationContext):
        print(ctx.getChildCount(), 'child exit')
        pass

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
        pass
