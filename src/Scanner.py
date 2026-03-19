from Token import Token

class Scanner():
    def __init__(self:Scanner, line:str) -> Scanner:
        self.line:str = line
        self.tokens = list[Token] = []
        self.index = 0

    def scan(self:Scanner) -> list[Token]:
        pass

    def scan_tokens(self:Scanner) -> None:
        pass

    def _current_value(self:Scanner) -> str:
        return self.line[self.index]

    def _next_index(self:Scanner) -> None:
        self.index += 1

    def _lookahead(self:Scanner) -> str:
        if self._end_of_line():
            return "\0"
        
        return self._current_value()

    def _match(self:Scanner, expected:str) -> bool:
        neightbor = self._lookahead()
        if neightbor != expected:
            return False

        self._next_index()
        return True

    def _end_of_line(self:Scanner) -> int:
        return self.index >= len(self.line)
