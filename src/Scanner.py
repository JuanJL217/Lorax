from Token import Token

class Scanner():
    def __init__(self:Scanner, line:str) -> Scanner:
        self.line:str = line
        self.tokens = list[Token] = []
        self.current_index = 0

    def scan(self:Scanner) -> list[Token]:
        pass

    def scan_tokens(self:Scanner) -> None:
        pass

    def _current_value(self:Scanner) -> str:
        return self.line[self.current_index]

    def _next_current_value(self:Scanner) -> None:
        self.current_index += 1

    def _lookahead(self:Scanner) -> str:
        if self._end_of_line():
            return "\0"
        
        return self._current_value()

    def _match(self:Scanner, expected:str) -> bool:
        neightbor = self._lookahead()
        if not neightbor == expected:
            return False

        self._next_current_value()
        return True

    def _end_of_line(self:Scanner) -> int:
        return self.current >= len(self.line)