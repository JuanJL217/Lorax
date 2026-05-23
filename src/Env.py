from typing import Optional


class Env(object):
    def __init__(self, *, enclosing: Optional["Env"] = None):
        self.values: dict[str, object] = {}
        self.enclosing: Optional["Env"] = enclosing

    def __repr__(self) -> str:
        all_values = str(self.values)
        enclosing = self.enclosing
        while enclosing is not None:
            all_values += " << " + str(enclosing.values)
            enclosing = enclosing.enclosing
        return all_values

    def ancestor(self, distance: int) -> "Env":
        env = self
        for _ in range(distance):
            if not env.enclosing:
                raise RuntimeError(
                    f"No enclosing environment found for {self} at distance {distance}"
                )
            env = env.enclosing
        return env

    def define(self, name: str, value: object):
        self.values[name] = value

    def get(self, name: str, distance: int | None = None) -> object:
        if distance is not None:
            scope = self.ancestor(distance)
            if name in scope.values:
                return scope.values[name]
        else:
            scope = self
            while scope is not None:
                if name in scope.values:
                    return scope.values[name]
                scope = scope.enclosing

        raise RuntimeError(f"Undefined variable '{name}'")

    def assign(self, name: str, value: object, distance: int | None = None) -> object:
        if distance is not None:
            scope = self.ancestor(distance)
            if name in scope.values:
                scope.values[name] = value
                return value
        else:
            scope = self
            while scope is not None:
                if name in scope.values:
                    scope.values[name] = value
                    return value
                scope = scope.enclosing

        raise RuntimeError(f"Cannot assign to undefined variable '{name}'")