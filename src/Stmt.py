from .Expr import Expr
from .Token import Token

class Stmt:
    pass

class ExpressionStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def __repr__(self) -> str:
        return f"{self.expression};"

class PrintStmt(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def __repr__(self) -> str:
        return f"print {self.expression};"

class BlockStmt(Stmt):
    def __init__(self, statements: list[Stmt]):
        self.statements = statements

    def __repr__(self) -> str:
        content = "; ".join(map(str, self.statements))
        return f"{{ {content} }}"

class VarDecl(Stmt):
    def __init__(self, name: Token, initializer: Expr | None):
        self.name = name
        self.initializer = initializer

    def __repr__(self) -> str:
        init = f" = {self.initializer}" if self.initializer else ""
        return f"var {self.name.lexeme}{init};"

class FunDecl(Stmt):
    def __init__(self, name: Token, parameters: list[Token], body: list[Stmt]):
        self.name = name
        self.parameters = parameters
        self.body = body

    def __repr__(self) -> str:
        params = ", ".join(p.lexeme for p in self.parameters)
        body = "; ".join(map(str, self.body))
        return f"fun {self.name.lexeme}({params}) {{ {body} }}"

class ReturnStmt(Stmt):
    def __init__(self, value: Expr | None):
        self.value = value

    def __repr__(self) -> str:
        return f"return {self.value or 'nil'};"

class IfStmt(Stmt):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
        
    def __repr__(self) -> str:
        res = f"if ({self.condition}) {self.thenBranch}"
        if self.elseBranch:
            res += f" else {self.elseBranch}"
        return res

class WhileStmt(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def __repr__(self) -> str:
        return f"while ({self.condition}) {self.body}"