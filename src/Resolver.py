from functools import singledispatchmethod
from .Interpreter import Interpreter
from .Stmt import (
    Stmt, ExpressionStmt, PrintStmt, VarDecl,
    FunDecl, BlockStmt, IfStmt, WhileStmt, ReturnStmt
)
from .Expr import (
    Expr, BinaryExpr, GroupingExpr, LiteralExpr,
    UnaryExpr, VariableExpr, AssignmentExpr, LogicExpr, CallExpr
)

class Resolver:
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: str):
        if not self.scopes: return
        scope = self.scopes[-1]
        if name in scope:
            print(f"Error: Ya existe una variable con el nombre '{name}' en este ámbito.")
        scope[name] = False

    def define(self, name: str):
        if not self.scopes: return
        self.scopes[-1][name] = True

    @singledispatchmethod
    def resolve(self, node: Stmt | Expr):
        raise RuntimeError(f"Tipo de nodo desconocido para el Resolver: {type(node)}")

    # --- Sentencias ---
    @resolve.register(BlockStmt)
    def _(self, stmt: BlockStmt):
        self.begin_scope()
        for s in stmt.statements:
            self.resolve(s)
        self.end_scope()

    @resolve.register(VarDecl)
    def _(self, stmt: VarDecl):
        self.declare(stmt.name.lexeme)
        if stmt.initializer:
            self.resolve(stmt.initializer)
        self.define(stmt.name.lexeme)

    @resolve.register(FunDecl)
    def _(self, stmt: FunDecl):
        self.declare(stmt.name.lexeme)
        self.define(stmt.name.lexeme)
        self.begin_scope()
        for param in stmt.parameters:
            self.declare(param.lexeme)
            self.define(param.lexeme)
        for s in stmt.body:
            self.resolve(s)
        self.end_scope()

    @resolve.register(ExpressionStmt)
    def _(self, stmt: ExpressionStmt):
        self.resolve(stmt.expression)

    @resolve.register(PrintStmt)
    def _(self, stmt: PrintStmt):
        self.resolve(stmt.expression)

    @resolve.register(IfStmt)
    def _(self, stmt: IfStmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.thenBranch)
        if stmt.elseBranch: self.resolve(stmt.elseBranch)

    @resolve.register(WhileStmt)
    def _(self, stmt: WhileStmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    @resolve.register(ReturnStmt)
    def _(self, stmt: ReturnStmt):
        if stmt.value: self.resolve(stmt.value)

    # --- Expresiones ---
    @resolve.register(VariableExpr)
    def _(self, expr: VariableExpr):
        if self.scopes and self.scopes[-1].get(expr.name.lexeme) is False:
            print(f"Error: No se puede leer la variable local '{expr.name.lexeme}' en su propio inicializador.")
        self._resolve_local(expr, expr.name.lexeme)

    @resolve.register(AssignmentExpr)
    def _(self, expr: AssignmentExpr):
        self.resolve(expr.value)
        self._resolve_local(expr, expr.name.lexeme)

    @resolve.register(BinaryExpr)
    def _(self, expr: BinaryExpr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    @resolve.register(LogicExpr)
    def _(self, expr: LogicExpr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    @resolve.register(GroupingExpr)
    def _(self, expr: GroupingExpr):
        self.resolve(expr.expression)

    @resolve.register(UnaryExpr)
    def _(self, expr: UnaryExpr):
        self.resolve(expr.right)

    @resolve.register(CallExpr)
    def _(self, expr: CallExpr):
        self.resolve(expr.callee)
        for arg in expr.arguments:
            self.resolve(arg)

    @resolve.register(LiteralExpr)
    def _(self, expr: LiteralExpr):
        pass

    def _resolve_local(self, expr: Expr, name: str):
        for i in range(len(self.scopes) - 1, -1, -1):
            if name in self.scopes[i]:
                self.interpreter.resolve_depth(expr, len(self.scopes) - 1 - i)
                return