from enum import auto, Enum
from typing import Union

class TokenType(Enum):

    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # Comments
    SLASH = auto()

    # Single character tokens
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    SEMICOLON = auto()
    STAR = auto()

    # One or two character tokens
    PLUS = auto()
    PLUS_PLUS = auto()
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    QUESTION = auto()
    COLON = auto()
    STAR_STAR = auto()

    # reserved words
    AND = auto()
    ELSE = auto()
    FALSE = auto()
    FUN = auto()
    FOR = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()
    # EXIT = auto()

    # end file
    EOF = auto()

TokenLiteralType = Union[float, str, bool, None]

class Token():
    def __init__(self, token_type:TokenType, lexeme:str, literal:TokenLiteralType):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal # this is the real value. That could be float, str, bool or None

    def __repr__(self) -> str:
        f"{self.token_type.name} asdasd"
        return f"{self.token_type.name}"
    
KeyWords = {
    "and": TokenType.AND,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "fun": TokenType.FUN,
    "for": TokenType.FOR,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
    # "exit": TokenType.EXIT
}