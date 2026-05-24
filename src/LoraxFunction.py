from .Env import Env
from .Constants import THIS_BINDING

class Return(Exception):
    def __init__(self, value):
        self.value = value

class LoraxFunction:
    def __init__(self, declaration, closure, is_initializer=False):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def arity(self):
        return len(self.declaration.parameters)

    def bind(self, instance):
        environment = Env(enclosing=self.closure)
        environment.define(THIS_BINDING, instance)
        return LoraxFunction(self.declaration, environment, self.is_initializer)

    def call(self, interpreter, arguments):
        environment = Env(enclosing=self.closure)
        for i, param in enumerate(self.declaration.parameters):
            environment.define(param.lexeme, arguments[i])
        
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as return_value:
            if self.is_initializer:
                return self.closure.get(THIS_BINDING)
            return return_value.value
            
        if self.is_initializer:
            return self.closure.get(THIS_BINDING)
        return None

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"