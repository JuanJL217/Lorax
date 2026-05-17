from .Token import Token, TokenType, TokenKeywords

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
            "[": TokenType.LEFT_BRACKET,
            "]": TokenType.RIGHT_BRACKET,
            ",": TokenType.COMMA,
            ";": TokenType.SEMICOLON,
            "%": TokenType.PERCENT,
            "?": TokenType.QUESTION,
            ":": TokenType.COLON,
        }

        self.double_tokens = {
            "=": (TokenType.EQUAL, TokenType.EQUAL_EQUAL),
            "!": (TokenType.BANG, TokenType.BANG_EQUAL),
            "<": (TokenType.LESS, TokenType.LESS_EQUAL),
            ">": (TokenType.GREATER, TokenType.GREATER_EQUAL),
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

        if c == ".":
            if self._lookahead().isdigit():
                raise Exception(f"Unexpected character: {c}")
            self._add_token(TokenType.DOT)
            return

        # Operadores dobles matemáticos
        if c == "+":
            self._add_token(TokenType.PLUS_PLUS if self._match("+") else TokenType.PLUS)
            return
        if c == "-":
            self._add_token(TokenType.MINUS_MINUS if self._match("-") else TokenType.MINUS)
            return
        if c == "*":
            self._add_token(TokenType.STAR_STAR if self._match("*") else TokenType.STAR)
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

        if c in self.double_tokens:
            simple, doble = self.double_tokens[c]
            token = doble if self._match("=") else simple
            self._add_token(token)
            return

        if c == "/":
            if self._match("/"):
                while self._lookahead() != "\n" and not self._end_of_line():
                    self._advance()

            elif self._match("*"):
                nesting = 1
                while nesting > 0 and not self._end_of_line():
                    if self._lookahead() == "/" and self._peek_next() == "*":
                        self._advance()
                        self._advance()
                        nesting += 1
                    elif self._lookahead() == "*" and self._peek_next() == "/":
                        self._advance()
                        self._advance()
                        nesting -= 1
                    else:
                        if self._lookahead() == "\n":
                            self.line_number += 1
                        self._advance()
                
                # Se atrapa los comentarios que nunca se cerraron
                if nesting > 0:
                    raise Exception("Unterminated comment")
            else:
                self._add_token(TokenType.SLASH)
            return

        # Soporte para strings con comillas dobles o simples
        if c in ('"', "'"):
            self._string(c)
            return

        raise Exception(f"Unexpected character: {c}")

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
            Token(token_type, lexeme=text, literal=literal, line=self.line_number)
        )

    def _number(self):
        while self._lookahead().isdigit():
            self._advance()

        # Si encontramos un punto, el siguiente caracter DEBE ser un dígito
        if self._lookahead() == ".":
            if self._peek_next().isdigit():
                self._advance()
                while self._lookahead().isdigit():
                    self._advance()
            else:
                raise Exception("Invalid number format")

        if self._is_alpha(self._lookahead()) or self._lookahead() == ".":
            raise Exception("Invalid number format")

        value = float(self.line[self.start:self.index])
        self._add_token(TokenType.NUMBER, value)

    def _identifier(self):
        while self._is_alphanum(self._lookahead()):
            self._advance()

        text = self.line[self.start:self.index]

        if text in TokenKeywords:
            self._add_token(TokenKeywords[text])
        else:
            self._add_token(TokenType.IDENTIFIER)

    def _string(self, quote_char: str):
        while self._lookahead() != quote_char and not self._end_of_line():
            if self._lookahead() == "\n":
                self.line_number += 1
            self._advance()

        if self._end_of_line():
            raise Exception("Unterminated string")

        self._advance() # Cerramos la comilla

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