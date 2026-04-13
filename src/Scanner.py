from Token import Token, TokenType, KeyWords


class Scanner:
    def __init__(self, line: str):
        self.line = line
        self.tokens: list[Token] = []
        self.index = 0
        self.start = 0
        self.line_number = 1

        self.single_tokens = {
            "(": TokenType.LEFT_PAREN,
            ")": TokenType.RIGHT_PAREN,
            "{": TokenType.LEFT_BRACE,
            "}": TokenType.RIGHT_BRACE,
            ",": TokenType.COMMA,
            ".": TokenType.DOT,
            "-": TokenType.MINUS,
            "+": TokenType.PLUS,
            ";": TokenType.SEMICOLON,
            "*": TokenType.STAR,
        }

    def scan(self) -> list[Token]:
        while not self._end_of_line():
            self.start = self.index
            self.scan_token()

        self._add_token(TokenType.EOF)
        return self.tokens

    def scan_token(self) -> None:
        c = self._advance()

        if c in " \t\r":
            return

        if c == "\n":
            self.line_number += 1
            return

        if c in self.single_tokens:
            self._add_token(self.single_tokens[c])
            return

        if c.isdigit():
            self._number()
            return

        if self._is_alpha(c):
            self._identifier()
            return

        if c == "=":
            token = TokenType.EQUAL_EQUAL if self._match("=") else TokenType.EQUAL
            self._add_token(token)
            return

        if c == "!":
            token = TokenType.BANG_EQUAL if self._match("=") else TokenType.BANG
            self._add_token(token)
            return

        if c == "<":
            token = TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS
            self._add_token(token)
            return

        if c == ">":
            token = TokenType.GREATER_EQUAL if self._match("=") else TokenType.GREATER
            self._add_token(token)
            return

        if c == "/":
            if self._match("/"):
                while self._lookahead() != "\n" and not self._end_of_line():
                    self._advance()
            else:
                self._add_token(TokenType.SLASH)
            return

        if c == '"':
            self._string()
            return

        raise Exception(f"Caracter inesperado: {c}")

    def _advance(self) -> str:
        c = self.line[self.index]
        self.index += 1
        return c

    def _lookahead(self) -> str:
        if self._end_of_line():
            return "\0"
        return self.line[self.index]

    def _match(self, expected: str) -> bool:
        if self._lookahead() != expected:
            return False
        self.index += 1
        return True

    def _end_of_line(self) -> bool:
        return self.index >= len(self.line)

    def _add_token(self, token_type, literal=None):
        text = self.line[self.start:self.index]
        self.tokens.append(
            Token(token_type, lexeme=text, literal=literal)
        )

    def _number(self):
        while self._lookahead().isdigit():
            self._advance()

        if self._lookahead() == "." and self._peek_next().isdigit():
            self._advance()
            while self._lookahead().isdigit():
                self._advance()

        value = float(self.line[self.start:self.index])
        self._add_token(TokenType.NUMBER, value)

    def _identifier(self):
        while self._is_alphanum(self._lookahead()):
            self._advance()

        text = self.line[self.start:self.index]

        if text in KeyWords:
            self._add_token(KeyWords[text])
        else:
            self._add_token(TokenType.IDENTIFIER)

    def _string(self):
        while self._lookahead() != '"' and not self._end_of_line():
            if self._lookahead() == "\n":
                self.line_number += 1
            self._advance()

        if self._end_of_line():
            raise Exception("String sin cerrar")

        self._advance()

        value = self.line[self.start + 1 : self.index - 1]
        self._add_token(TokenType.STRING, value)

    def _peek_next(self):
        if self.index + 1 >= len(self.line):
            return "\0"
        return self.line[self.index + 1]

    def _is_alpha(self, c):
        return c.isalpha() or c == "_"

    def _is_alphanum(self, c):
        return c.isalnum() or c == "_"