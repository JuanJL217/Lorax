from .LoraxInstance import LoraxInstance

class LoraxClass:
    def __init__(self, name: str, superclass: 'LoraxClass | None', methods: dict):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def find_method(self, name: str):
        if name in self.methods:
            return self.methods[name]
        if self.superclass:
            return self.superclass.find_method(name)
        return None

    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer:
            return initializer.arity()
        return 0

    def call(self, interpreter, args: list) -> LoraxInstance:
        instance = LoraxInstance(self)
        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, args)
        return instance

    def __str__(self) -> str:
        return self.name
