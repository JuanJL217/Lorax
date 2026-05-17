from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Interpreter import Interpreter

from .Stmt import FunDecl
from .Env import Env


class ReturnValue(Exception):
    def __init__(self, value: object):
        super().__init__(f"Return Value: {value}")
        self.value = value


class Function(object):
    def __init__(
        self,
        declaration: FunDecl,
        closure_env: Env,
    ):
        self.closure_env = closure_env
        self.declaration = declaration
        self.arity = len(declaration.parameters)

    def __call__(self, interpreter: "Interpreter", arguments: list):
        function_env = Env(enclosing=self.closure_env)

        for param, arg in zip(self.declaration.parameters, arguments):
            function_env.define(param.lexeme, arg)

        try:
            interpreter.execute_block(self.declaration.body, function_env)
        except ReturnValue as returnvalue:
            return returnvalue.value
        return None

    def __repr__(self) -> str:
        params = ", ".join(param.lexeme for param in self.declaration.parameters)
        return f"<fn {self.declaration.name.lexeme}({params})>"