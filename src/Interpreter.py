from .Expr import *
from .Stmt import *
from .Token import TokenType
from .Env import Env

_EXPR_MAP = {}
_STMT_MAP = {}

def register_expr(cls):
    def decorator(func):
        _EXPR_MAP[cls] = func
        return func
    return decorator

def register_stmt(cls):
    def decorator(func):
        _STMT_MAP[cls] = func
        return func
    return decorator

class NativeType:
    def arity(self): return 1
    def call(self, interpreter, args):
        val = args[0]
        if val is None: return "nil"
        if isinstance(val, bool): return "bool"
        if isinstance(val, (int, float)): return "number"
        if isinstance(val, str): return "string"
        return "builtin function"
    def __str__(self): return "builtin function"

class NativeLen:
    def arity(self): return 1
    def call(self, interpreter, args):
        val = args[0]
        if not isinstance(val, str):
            raise RuntimeError("Argument of `len` must be a string")
        return float(len(val))

class Interpreter:
    def __init__(self):
        self.globals = Env()
        self.env = self.globals
        self.local_scope_depths = {}
        
        self.globals.define("type", NativeType())
        self.globals.define("len", NativeLen())

    def interpret(self, statements):
        for stmt in statements:
            self.execute(stmt)

    def execute(self, stmt):
        processor = _STMT_MAP.get(type(stmt))
        if processor:
            processor(self, stmt)
        else:
            raise RuntimeError(f"Unknown statement type: {type(stmt)}")

    def evaluate(self, expr: Expr):
        processor = _EXPR_MAP.get(type(expr))
        if processor:
            return processor(self, expr)
        raise RuntimeError(f"Unknown expression type: {type(expr)}")

    def resolve_depth(self, expr, depth):
        self.local_scope_depths[expr] = depth

    def _is_truthy(self, obj):
        if obj is None: return False
        if isinstance(obj, bool): return obj
        return True

    def _check_number_operand(self, operator, operand, msg="Operand must be a number"):
        if isinstance(operand, (int, float)): return
        raise RuntimeError(msg)

    def _check_number_operands(self, operator, left, right, msg="Operands must be numbers"):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)): return
        raise RuntimeError(msg)


@register_expr(LiteralExpr)
def _visit_literal(interpreter, expr):
    return expr.value

@register_expr(GroupingExpr)
def _visit_grouping(interpreter, expr):
    return interpreter.evaluate(expr.expression)

@register_expr(VariableExpr)
def _visit_variable(interpreter, expr):
    distance = interpreter.local_scope_depths.get(expr)
    return interpreter.env.get(expr.name.lexeme, distance)

@register_expr(UnaryExpr)
def _visit_unary(interpreter, expr):
    right = interpreter.evaluate(expr.right)
    op = expr.operator.token_type
    
    if op == TokenType.MINUS:
        interpreter._check_number_operand(expr.operator, right, "Operand of - must be a number")
        return -float(right)
    if op == TokenType.BANG:
        return not interpreter._is_truthy(right)
    if op == TokenType.NUMBER_CAST:
        if right is None: 
            raise RuntimeError("Cannot cast nil to number")
        try: 
            return float(right)
        except ValueError: 
            raise RuntimeError("Cannot cast string")
    if op == TokenType.STRING_CAST:
        if right is None: return "nil"
        if isinstance(right, bool): return "true" if right else "false"
        return str(right)
    if op == TokenType.BOOL_CAST:
        return interpreter._is_truthy(right)

@register_expr(BinaryExpr)
def _visit_binary(interpreter, expr):
    left = interpreter.evaluate(expr.left)
    right = interpreter.evaluate(expr.right)
    op = expr.operator.token_type

    if op == TokenType.PLUS:
        if isinstance(left, str) and isinstance(right, str): return left + right
        if isinstance(left, (int, float)) and isinstance(right, (int, float)): return left + right
        raise RuntimeError("Operands of + must be either numbers or strings")
    
    if op == TokenType.MINUS:
        interpreter._check_number_operands(expr.operator, left, right, "Operands of - must be numbers")
        return left - right
    if op == TokenType.STAR:
        interpreter._check_number_operands(expr.operator, left, right)
        return left * right
    if op == TokenType.SLASH:
        interpreter._check_number_operands(expr.operator, left, right)
        if right == 0: raise RuntimeError("Division by 0")
        return left / right
    if op == TokenType.PERCENT:
        interpreter._check_number_operands(expr.operator, left, right)
        if right == 0: raise RuntimeError("Modulo by 0")
        return left % right
    if op == TokenType.STAR_STAR:
        interpreter._check_number_operands(expr.operator, left, right)
        return left ** right

    if op == TokenType.GREATER: return left > right
    if op == TokenType.GREATER_EQUAL: return left >= right
    if op == TokenType.LESS: return left < right
    if op == TokenType.LESS_EQUAL: return left <= right
    if op == TokenType.BANG_EQUAL: return left != right
    if op == TokenType.EQUAL_EQUAL: return left == right

@register_expr(TernaryExpr)
def _visit_ternary(interpreter, expr):
    if interpreter._is_truthy(interpreter.evaluate(expr.condition)):
        return interpreter.evaluate(expr.true_branch)
    return interpreter.evaluate(expr.false_branch)

@register_expr(IndexExpr)
def _visit_index(interpreter, expr):
    target = interpreter.evaluate(expr.target)
    index = interpreter.evaluate(expr.index)
    
    if not isinstance(target, str): 
        raise RuntimeError("Only strings can be indexed")
    if not isinstance(index, (int, float)) or index < 0 or index % 1 != 0:
        raise RuntimeError("Index must be a positive whole number")
    if int(index) >= len(target):
        raise RuntimeError("Index out of range")
        
    return target[int(index)]

@register_expr(CallExpr)
def _visit_call(interpreter, expr):
    callee = interpreter.evaluate(expr.callee)
    args = [interpreter.evaluate(arg) for arg in expr.arguments]
    
    if not hasattr(callee, 'call'):
        raise RuntimeError("Can only call functions")
        
    return callee.call(interpreter, args)
    
@register_expr(LogicExpr)
def _visit_logic(interpreter, expr):
    left = interpreter.evaluate(expr.left)
    if expr.operator.token_type == TokenType.OR:
        if interpreter._is_truthy(left): return left
    else:
        if not interpreter._is_truthy(left): return left
    return interpreter.evaluate(expr.right)