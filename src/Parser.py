from .Token import Token, TokenType
from .Expr import (
    Expr, BinaryExpr, GroupingExpr, LiteralExpr, UnaryExpr,
    VariableExpr, AssignmentExpr, LogicExpr, CallExpr,
    TernaryExpr, IndexExpr, PostfixExpr, PrefixExpr
)
from .Stmt import (
    Stmt, PrintStmt, ExpressionStmt, BlockStmt, VarDecl,
    FunDecl, IfStmt, WhileStmt, ReturnStmt,
)

class Parser(object):
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> list[Stmt]:
        statements = []
        while not self._is_at_end():
            statements.append(self.statement())
        return statements

    def statement(self) -> Stmt:
        if self._match(TokenType.VAR): return self.variable_declaration()
        if self._match(TokenType.FUN): return self.function_declaration()
        if self._match(TokenType.RETURN): return self.return_statement()
        if self._match(TokenType.IF): return self.if_statement()
        if self._match(TokenType.WHILE): return self.while_statement()
        if self._match(TokenType.FOR): return self.for_statement()
        if self._match(TokenType.LEFT_BRACE): return self.block_statement()
        if self._match(TokenType.PRINT): return self.print_statement()
        
        return self.expression_statement()

    def expression_statement(self) -> ExpressionStmt:
        expr = self.expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after expression")
        return ExpressionStmt(expr)

    def print_statement(self) -> PrintStmt:
        value = self.expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after value to print")
        return PrintStmt(value)

    def block_statement(self) -> BlockStmt:
        return BlockStmt(self.block())

    def block(self) -> list[Stmt]:
        statements = []
        while not self._is_at_end() and self._lookahead().token_type != TokenType.RIGHT_BRACE:
            statements.append(self.statement())

        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after block")
        return statements

    def while_statement(self) -> WhileStmt:
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'")
        condition = self.expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after condition")
        body = self.statement()
        return WhileStmt(condition, body)

    def if_statement(self) -> IfStmt:
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'")
        condition = self.expression()
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after condition")
        
        then_branch = self.statement()
        else_branch = self.statement() if self._match(TokenType.ELSE) else None
        
        return IfStmt(condition, then_branch, else_branch)

    def for_statement(self) -> Stmt:
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'")

        initializer = None
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self.variable_declaration()
        else:
            initializer = self.expression_statement()

        condition = self.expression() if not self._check(TokenType.SEMICOLON) else LiteralExpr(True)
        self._consume(TokenType.SEMICOLON, "Expected ';' after loop condition")

        increment = self.expression() if not self._check(TokenType.RIGHT_PAREN) else None
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after for clauses")

        body = self.statement()

        if increment:
            body = BlockStmt([body, ExpressionStmt(increment)])
        
        body = WhileStmt(condition, body)
        
        if initializer:
            body = BlockStmt([initializer, body])

        return body

    def return_statement(self) -> ReturnStmt:
        value = self.expression() if not self._check(TokenType.SEMICOLON) else None
        self._consume(TokenType.SEMICOLON, "Expected ';' after return value")
        return ReturnStmt(value)

    def function_declaration(self) -> FunDecl:
        name = self._consume(TokenType.IDENTIFIER, "Expected function name")
        self._consume(TokenType.LEFT_PAREN, "Expected '(' after function name")
        
        parameters = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                parameters.append(self._consume(TokenType.IDENTIFIER, "Expected parameter name"))
                if not self._match(TokenType.COMMA): break
        
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters")
        self._consume(TokenType.LEFT_BRACE, "Expected '{' before function body")
        
        return FunDecl(name, parameters, self.block())

    def variable_declaration(self) -> VarDecl:
        name = self._consume(TokenType.IDENTIFIER, "Expected variable name")
        initializer = self.expression() if self._match(TokenType.EQUAL) else None
        self._consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        return VarDecl(name, initializer)

    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self) -> Expr:
        expr = self.ternary()
        if self._match(TokenType.EQUAL):
            value = self.assignment()
            if isinstance(expr, VariableExpr):
                return AssignmentExpr(expr.name, value)
            raise SyntaxError("Invalid assignment target")
        return expr

    def ternary(self) -> Expr:
        expr = self.logic_or()
        if self._match(TokenType.QUESTION):
            true_branch = self.ternary()
            self._consume(TokenType.COLON, "Expected ':' after ternary condition")
            false_branch = self.ternary()
            return TernaryExpr(expr, true_branch, false_branch)
        return expr

    def logic_or(self) -> Expr:
        expr = self.logic_and()
        while self._match(TokenType.OR):
            expr = LogicExpr(expr, self._previous(), self.logic_and())
        return expr

    def logic_and(self) -> Expr:
        expr = self.equality()
        while self._match(TokenType.AND):
            expr = LogicExpr(expr, self._previous(), self.equality())
        return expr

    def equality(self) -> Expr:
        expr = self.comparison()
        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            expr = BinaryExpr(expr, self._previous(), self.comparison())
        return expr

    def comparison(self) -> Expr:
        expr = self.term()
        while self._match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            expr = BinaryExpr(expr, self._previous(), self.term())
        return expr

    def term(self) -> Expr:
        expr = self.factor()
        while self._match(TokenType.MINUS, TokenType.PLUS):
            expr = BinaryExpr(expr, self._previous(), self.factor())
        return expr

    def factor(self) -> Expr:
        expr = self.power()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            expr = BinaryExpr(expr, self._previous(), self.power())
        return expr

    def power(self) -> Expr:
        expr = self.unary()
        if self._match(TokenType.STAR_STAR):
            expr = BinaryExpr(expr, self._previous(), self.power())
        return expr

    def unary(self) -> Expr:
        if self._match(TokenType.PLUS_PLUS, TokenType.MINUS_MINUS):
            op = self._previous()
            right = self.unary()
            
            if isinstance(right, VariableExpr):
                math_op = TokenType.PLUS if op.token_type == TokenType.PLUS_PLUS else TokenType.MINUS
                op_token = Token(math_op, op.lexeme[0], None, op.line)
                value = BinaryExpr(right, op_token, LiteralExpr(1.0))
                return AssignmentExpr(right.name, value)
            
            if op.token_type == TokenType.MINUS_MINUS:
                single_token = Token(TokenType.MINUS, "-", None, op.line)
                return UnaryExpr(single_token, UnaryExpr(single_token, right))
            
            raise SyntaxError("Invalid prefix target")

        if self._match(TokenType.BANG, TokenType.MINUS, TokenType.NUMBER_CAST, TokenType.STRING_CAST, TokenType.BOOL_CAST):
            return UnaryExpr(self._previous(), self.unary())
        
        return self.call()

    def call(self) -> Expr:
        expr = self.primary()
        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.LEFT_BRACKET):
                index = self.expression()
                self._consume(TokenType.RIGHT_BRACKET, "Expected ']' after index")
                expr = IndexExpr(expr, index)
            elif self._match(TokenType.PLUS_PLUS, TokenType.MINUS_MINUS):
                if not isinstance(expr, (VariableExpr, IndexExpr)):
                    raise SyntaxError("Invalid postfix target")
                expr = PostfixExpr(expr, self._previous())
            else:
                break
        return expr

    def _finish_call(self, callee: Expr) -> Expr:
        arguments = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                arguments.append(self.expression())
                if not self._match(TokenType.COMMA): break
        
        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments")
        return CallExpr(callee, arguments)

    def primary(self) -> Expr:
        if self._match(TokenType.FALSE): return LiteralExpr(False)
        if self._match(TokenType.TRUE): return LiteralExpr(True)
        if self._match(TokenType.NIL): return LiteralExpr(None)
        if self._match(TokenType.NUMBER, TokenType.STRING): return LiteralExpr(self._previous().literal)
        if self._match(TokenType.IDENTIFIER): return VariableExpr(self._previous())

        if self._match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after expression")
            return GroupingExpr(expr)

        raise SyntaxError(f"Expected expression, got `{self._lookahead()}`")

    def _is_at_end(self) -> bool:
        return self._lookahead().token_type == TokenType.EOF

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _lookahead(self) -> Token:
        return self.tokens[self.current]

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end(): return False
        return self._lookahead().token_type == token_type

    def _advance(self) -> Token:
        if not self._is_at_end(): self.current += 1
        return self._previous()

    def _match(self, *token_types: TokenType) -> bool:
        for t in token_types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type): return self._advance()
        raise SyntaxError(f"{message}, got `{self._lookahead()}`")