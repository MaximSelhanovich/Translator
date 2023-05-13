from CPP14ParserVisitor import CPP14ParserVisitor
from CPP14Parser import CPP14Parser
class CustomCPP14ParserVisitor(CPP14ParserVisitor):

    # Visit a parse tree produced by CPP14Parser#multiplicativeExpression.
    def visitMultiplicativeExpression(self, ctx:CPP14Parser.MultiplicativeExpressionContext):
        result = self.visit(ctx.getChild(0))
        for expr in range(1, ctx.getChildCount()):
            right = None

        return self.visitChildren(ctx)


    # Visit a parse tree produced by CPP14Parser#additiveExpression.
    def visitAdditiveExpression(self, ctx:CPP14Parser.AdditiveExpressionContext):
        return self.visitChildren(ctx)