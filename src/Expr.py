from .Token import Token, TokenLiteralType

class Expr:
    pass

class BinaryExpr(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"({self.left} {self.operator.lexeme} {self.right})"

class GroupingExpr(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def __repr__(self) -> str:
        return f"(group {self.expression})"

class LiteralExpr(Expr):
    def __init__(self, value: TokenLiteralType):
        self.value = value

    def __repr__(self) -> str:
        if self.value is None: return "nil"
        return str(self.value)

class UnaryExpr(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"({self.operator.lexeme} {self.right})"

class VariableExpr(Expr):
    def __init__(self, name: Token):
        self.name = name

    def __repr__(self) -> str:
        return f"var {self.name.lexeme}"

class AssignmentExpr(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return f"{self.name.lexeme} = {self.value}"

class LogicExpr(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right
        
    def __repr__(self) -> str:
        return f"({self.left} {self.operator.lexeme} {self.right})"

class CallExpr(Expr):
    def __init__(self, callee: Expr, arguments: list[Expr]):
        self.callee = callee
        self.arguments = arguments
        
    def __repr__(self) -> str:
        args = ", ".join(str(arg) for arg in self.arguments)
        return f"call {self.callee}({args})"

class TernaryExpr(Expr):
    def __init__(self, condition: Expr, true_branch: Expr, false_branch: Expr):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def __repr__(self) -> str:
        return f"({self.condition} ? {self.true_branch} : {self.false_branch})"

class IndexExpr(Expr):
    def __init__(self, target: Expr, index: Expr):
        self.target = target
        self.index = index

    def __repr__(self) -> str:
        return f"({self.target}[{self.index}])"

class PostfixExpr(Expr):
    def __init__(self, left: Expr, operator: Token):
        self.left = left
        self.operator = operator

    def __repr__(self) -> str:
        return f"({self.left}{self.operator.lexeme})"

class PrefixExpr(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"({self.operator.lexeme}{self.right})"

class GetExpr(Expr):
    def __init__(self, object: Expr, name: Token):
        self.object = object
        self.name = name

    def __repr__(self) -> str:
        return f"{self.object}.{self.name.lexeme}"

class SetExpr(Expr):
    def __init__(self, object: Expr, name: Token, value: Expr):
        self.object = object
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return f"{self.object}.{self.name.lexeme} = {self.value}"

class ThisExpr(Expr):
    def __init__(self, keyword: Token):
        self.keyword = keyword

    def __repr__(self) -> str:
        return "this"

class SuperExpr(Expr):
    def __init__(self, keyword: Token, method: Token):
        self.keyword = keyword
        self.method = method

    def __repr__(self) -> str:
        return f"super.{self.method.lexeme}"

class ListExpr(Expr):
    def __init__(self, elements: list[Expr]):
        self.elements = elements

    def __repr__(self) -> str:
        return f"[{', '.join(str(e) for e in self.elements)}]"

class IndexSetExpr(Expr):
    def __init__(self, target: Expr, index: Expr, value: Expr):
        self.target = target
        self.index = index
        self.value = value

    def __repr__(self) -> str:
        return f"{self.target}[{self.index}] = {self.value}"

class DictExpr(Expr):
    def __init__(self, keys: list[Expr], values: list[Expr]):
        self.keys = keys
        self.values = values

    def __repr__(self) -> str:
        pairs = [f"{k}: {v}" for k, v in zip(self.keys, self.values)]
        return f"{{{', '.join(pairs)}}}"