from functools import singledispatchmethod
from .Expr import *
from .Stmt import *
from .Token import TokenType
from .Env import Env
from .LoraxClass import LoraxClass
from .LoraxInstance import LoraxInstance
from .LoraxFunction import LoraxFunction, Return

class NativeType:
    def arity(self): return 1
    def call(self, interpreter, args):
        val = args[0]
        if val is None: return "nil"
        if isinstance(val, bool): return "bool"
        if isinstance(val, (int, float)): return "number"
        if isinstance(val, str): return "string"
        if isinstance(val, list): return "list"
        if isinstance(val, dict): return "hash"
        if isinstance(val, LoraxInstance):
            return val.klass.name
        if isinstance(val, LoraxClass):
            return "class"
        return "builtin function"
    def __str__(self): return "builtin function"

class NativeLen:
    def arity(self): return 1
    def call(self, interpreter, args):
        val = args[0]
        if not isinstance(val, (str, list, dict)):
            raise RuntimeError("Argument of `len` must be a string, list or hash")
        return float(len(val))

class NativeAppend:
    def arity(self): return 2
    def call(self, interpreter, args):
        if not isinstance(args[0], list):
            raise RuntimeError("First argument of `append` must be a list")
        args[0].append(args[1])
        return args[0]

class NativeHas:
    def arity(self): return 2
    def call(self, interpreter, args):
        if not isinstance(args[0], dict):
            raise RuntimeError("First argument of `has` must be a hash")
        return args[1] in args[0]

class NativeKeys:
    def arity(self): return 1
    def call(self, interpreter, args):
        if not isinstance(args[0], dict):
            raise RuntimeError("Argument of `keys` must be a hash")
        return list(args[0].keys())

class NativePop:
    def arity(self): return 2
    def call(self, interpreter, args):
        if not isinstance(args[0], list):
            raise RuntimeError("First argument of `pop` must be a list")
        index = args[1]
        if not isinstance(index, (int, float)) or index < 0 or index % 1 != 0:
            raise RuntimeError("Index must be a positive whole number")
        if int(index) >= len(args[0]):
            raise RuntimeError("Index out of range")
        return args[0].pop(int(index))

class BoundNativeMethod:
    def __init__(self, obj, method_name):
        self.obj = obj
        self.method_name = method_name
        self._arity = 0
        
        if isinstance(obj, list):
            if method_name in ("append", "pop"): self._arity = 1
            elif method_name == "len": self._arity = 0
            else: raise RuntimeError(f"Undefined property '{method_name}' on list.")
        elif isinstance(obj, dict):
            if method_name == "has": self._arity = 1
            elif method_name in ("keys", "len"): self._arity = 0
            else: raise RuntimeError(f"Undefined property '{method_name}' on hash.")
        elif isinstance(obj, str):
            if method_name == "len": self._arity = 0
            else: raise RuntimeError(f"Undefined property '{method_name}' on string.")
        else:
            raise RuntimeError("Invalid object for native methods.")

    def arity(self):
        return self._arity
        
    def call(self, interpreter, args):
        if isinstance(self.obj, list):
            if self.method_name == "append":
                self.obj.append(args[0])
                return self.obj
            if self.method_name == "pop":
                index = args[0]
                if not isinstance(index, (int, float)) or index < 0 or index % 1 != 0:
                    raise RuntimeError("Index must be a positive whole number")
                if int(index) >= len(self.obj):
                    raise RuntimeError("Index out of range")
                return self.obj.pop(int(index))
            if self.method_name == "len": return float(len(self.obj))
        elif isinstance(self.obj, dict):
            if self.method_name == "has": return args[0] in self.obj
            if self.method_name == "keys": return list(self.obj.keys())
            if self.method_name == "len": return float(len(self.obj))
        elif isinstance(self.obj, str):
            if self.method_name == "len": return float(len(self.obj))

    def __str__(self): return f"<native method {self.method_name}>"

class Interpreter:
    def __init__(self):
        self.globals = Env()
        self.env = self.globals
        self.local_scope_depths = {}
        
        self.globals.define("type", NativeType())
        self.globals.define("len", NativeLen())
        self.globals.define("append", NativeAppend())
        self.globals.define("has", NativeHas())
        self.globals.define("keys", NativeKeys())
        self.globals.define("pop", NativePop())

    def interpret(self, statements):
        for stmt in statements:
            self.execute(stmt)

    @singledispatchmethod
    def execute(self, stmt: Stmt):
        raise RuntimeError(f"Unknown statement type: {type(stmt)}")

    @singledispatchmethod
    def evaluate(self, expr: Expr):
        raise RuntimeError(f"Unknown expression type: {type(expr)}")

    def execute_block(self, statements, env):
        previous = self.env
        try:
            self.env = env
            for statement in statements:
                self.execute(statement)
        finally:
            self.env = previous

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

    @evaluate.register(LiteralExpr)
    def _(self, expr: LiteralExpr):
        return expr.value

    @evaluate.register(GroupingExpr)
    def _(self, expr: GroupingExpr):
        return self.evaluate(expr.expression)

    @evaluate.register(VariableExpr)
    def _(self, expr: VariableExpr):
        distance = self.local_scope_depths.get(expr)
        return self.env.get(expr.name.lexeme, distance)

    @evaluate.register(AssignmentExpr)
    def _(self, expr: AssignmentExpr):
        value = self.evaluate(expr.value)
        distance = self.local_scope_depths.get(expr)
        self.env.assign(expr.name.lexeme, value, distance)
        return value

    @evaluate.register(UnaryExpr)
    def _(self, expr: UnaryExpr):
        right = self.evaluate(expr.right)
        op = expr.operator.token_type
        
        if op == TokenType.MINUS:
            self._check_number_operand(expr.operator, right, "Operand of - must be a number")
            return -float(right)
        if op == TokenType.BANG:
            return not self._is_truthy(right)
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
            return self._is_truthy(right)

    @evaluate.register(BinaryExpr)
    def _(self, expr: BinaryExpr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        op = expr.operator.token_type

        if op == TokenType.PLUS:
            if isinstance(left, str) and isinstance(right, str): return left + right
            if isinstance(left, (int, float)) and isinstance(right, (int, float)): return left + right
            raise RuntimeError("Operands of + must be either numbers or strings")
        
        if op == TokenType.MINUS:
            self._check_number_operands(expr.operator, left, right, "Operands of - must be numbers")
            return left - right
        if op == TokenType.STAR:
            self._check_number_operands(expr.operator, left, right)
            return left * right
        if op == TokenType.SLASH:
            self._check_number_operands(expr.operator, left, right)
            if right == 0: raise RuntimeError("Division by 0")
            return left / right
        if op == TokenType.PERCENT:
            self._check_number_operands(expr.operator, left, right)
            if right == 0: raise RuntimeError("Modulo by 0")
            return left % right
        if op == TokenType.STAR_STAR:
            self._check_number_operands(expr.operator, left, right)
            return left ** right

        if op == TokenType.GREATER: return left > right
        if op == TokenType.GREATER_EQUAL: return left >= right
        if op == TokenType.LESS: return left < right
        if op == TokenType.LESS_EQUAL: return left <= right
        if op == TokenType.BANG_EQUAL: return left != right
        if op == TokenType.EQUAL_EQUAL: return left == right

    @evaluate.register(TernaryExpr)
    def _(self, expr: TernaryExpr):
        if self._is_truthy(self.evaluate(expr.condition)):
            return self.evaluate(expr.true_branch)
        return self.evaluate(expr.false_branch)

    @evaluate.register(IndexExpr)
    def _(self, expr: IndexExpr):
        target = self.evaluate(expr.target)
        index = self.evaluate(expr.index)
        
        if not isinstance(target, (str, list, dict)): 
            raise RuntimeError("Only strings, lists, and dicts can be indexed")
            
        if isinstance(target, dict):
            if index not in target:
                raise RuntimeError(f"Key Error: '{index}'")
            return target[index]
            
        if not isinstance(index, (int, float)) or index < 0 or index % 1 != 0:
            raise RuntimeError("Index must be a positive whole number")
        if int(index) >= len(target):
            raise RuntimeError("Index out of range")
            
        return target[int(index)]

    @evaluate.register(IndexSetExpr)
    def _(self, expr: IndexSetExpr):
        target = self.evaluate(expr.target)
        index = self.evaluate(expr.index)
        value = self.evaluate(expr.value)
        
        if isinstance(target, dict):
            target[index] = value
            return value
            
        if not isinstance(target, list):
            raise RuntimeError("Only lists and dicts can be index-assigned")
        if not isinstance(index, (int, float)) or index < 0 or index % 1 != 0:
            raise RuntimeError("Index must be a positive whole number")
        if int(index) >= len(target):
            raise RuntimeError("Index out of range")
            
        target[int(index)] = value
        return value

    @evaluate.register(ListExpr)
    def _(self, expr: ListExpr):
        return [self.evaluate(e) for e in expr.elements]

    @evaluate.register(DictExpr)
    def _(self, expr: DictExpr):
        return {self.evaluate(k): self.evaluate(v) for k, v in zip(expr.keys, expr.values)}

    @evaluate.register(CallExpr)
    def _(self, expr: CallExpr):
        callee = self.evaluate(expr.callee)
        args = [self.evaluate(arg) for arg in expr.arguments]
        
        if not hasattr(callee, 'call'):
            raise RuntimeError("Can only call functions")
            
        if len(args) != callee.arity():
            raise RuntimeError(f"Expected {callee.arity()} arguments but got {len(args)}.")

        return callee.call(self, args)
        
    @evaluate.register(LogicExpr)
    def _(self, expr: LogicExpr):
        left = self.evaluate(expr.left)
        if expr.operator.token_type == TokenType.OR:
            if self._is_truthy(left): return left
        else:
            if not self._is_truthy(left): return left
        return self.evaluate(expr.right)

    @evaluate.register(PostfixExpr)
    def _(self, expr: PostfixExpr):
        value = self.evaluate(expr.left)
        self._check_number_operand(expr.operator, value, "Operand of postfix must be a number")
        
        increment = 1.0 if expr.operator.token_type == TokenType.PLUS_PLUS else -1.0
        new_value = value + increment
        
        if isinstance(expr.left, VariableExpr):
            distance = self.local_scope_depths.get(expr.left)
            self.env.assign(expr.left.name.lexeme, new_value, distance)
        elif isinstance(expr.left, GetExpr):
            obj = self.evaluate(expr.left.object)
            if not isinstance(obj, LoraxInstance):
                raise RuntimeError("Only instances have fields.")
            obj.set(expr.left.name, new_value)
        elif isinstance(expr.left, IndexExpr):
            target = self.evaluate(expr.left.target)
            index = self.evaluate(expr.left.index)
            if isinstance(target, dict):
                target[index] = new_value
            elif isinstance(target, list):
                target[int(index)] = new_value
            else:
                raise RuntimeError("Only lists and dicts can be index-assigned")
            
        return value

    @evaluate.register(ThisExpr)
    def _(self, expr: ThisExpr):
        distance = self.local_scope_depths.get(expr)
        return self.env.get(expr.keyword.lexeme, distance)

    @evaluate.register(SuperExpr)
    def _(self, expr: SuperExpr):
        distance = self.local_scope_depths.get(expr)
        if distance is None:
            raise RuntimeError("Cannot use 'super' outside of a method.")
        
        superclass = self.env.get("super", distance)
        obj = self.env.get("this", distance - 1)
        method = superclass.find_method(expr.method.lexeme)
        if not method:
            raise RuntimeError(f"Undefined property '{expr.method.lexeme}'.")
        return method.bind(obj)

    @evaluate.register(GetExpr)
    def _(self, expr: GetExpr):
        obj = self.evaluate(expr.object)
        if isinstance(obj, LoraxInstance):
            return obj.get(expr.name)
        if isinstance(obj, (list, dict, str)):
            return BoundNativeMethod(obj, expr.name.lexeme)
        raise RuntimeError("Only instances have properties.")

    @evaluate.register(SetExpr)
    def _(self, expr: SetExpr):
        obj = self.evaluate(expr.object)
        if not isinstance(obj, LoraxInstance):
            raise RuntimeError("Only instances have fields.")
        value = self.evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    @execute.register(ExpressionStmt)
    def _(self, stmt: ExpressionStmt):
        self.evaluate(stmt.expression)

    @execute.register(PrintStmt)
    def _(self, stmt: PrintStmt):
        value = self.evaluate(stmt.expression)
        print(value)

    @execute.register(ClassDecl)
    def _(self, stmt: ClassDecl):
        superclass = None
        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoraxClass):
                raise RuntimeError("Superclass must be a class.")
                
        environment = self.env
        if stmt.superclass is not None:
            environment = Env(enclosing=environment)
            environment.define("super", superclass)

        methods = {}
        for method in stmt.methods:
            is_initializer = method.name.lexeme == "init"
            function = LoraxFunction(method, environment, is_initializer)
            methods[method.name.lexeme] = function
        klass = LoraxClass(stmt.name.lexeme, superclass, methods)
        self.env.define(stmt.name.lexeme, klass)

    @execute.register(FunDecl)
    def _(self, stmt: FunDecl):
        function = LoraxFunction(stmt, self.env)
        self.env.define(stmt.name.lexeme, function)

    @execute.register(VarDecl)
    def _(self, stmt: VarDecl):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.env.define(stmt.name.lexeme, value)

    @execute.register(BlockStmt)
    def _(self, stmt: BlockStmt):
        self.execute_block(stmt.statements, Env(enclosing=self.env))

    @execute.register(IfStmt)
    def _(self, stmt: IfStmt):
        if self._is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    @execute.register(WhileStmt)
    def _(self, stmt: WhileStmt):
        while self._is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    @execute.register(ReturnStmt)
    def _(self, stmt: ReturnStmt):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise Return(value)