from enum import Enum, auto
from typing import Union

class TokenType(Enum):
    LEFT_PAREN = auto(); RIGHT_PAREN = auto()
    LEFT_BRACE = auto(); RIGHT_BRACE = auto()
    LEFT_BRACKET = auto(); RIGHT_BRACKET = auto()
    COMMA = auto(); DOT = auto(); MINUS = auto()
    PLUS = auto(); SEMICOLON = auto(); STAR = auto()
    SLASH = auto(); PERCENT = auto()

    BANG = auto(); BANG_EQUAL = auto()
    EQUAL = auto(); EQUAL_EQUAL = auto()
    GREATER = auto(); GREATER_EQUAL = auto()
    LESS = auto(); LESS_EQUAL = auto()

    STAR_STAR = auto()
    PLUS_PLUS = auto()
    MINUS_MINUS = auto()
    
    QUESTION = auto()
    COLON = auto()

    IDENTIFIER = auto(); STRING = auto(); NUMBER = auto()

    AND = auto(); ELSE = auto(); FALSE = auto()
    FUN = auto(); FOR = auto(); IF = auto()
    NIL = auto(); OR = auto(); PRINT = auto()
    RETURN = auto(); SUPER = auto(); THIS = auto()
    TRUE = auto(); VAR = auto(); WHILE = auto()

    NUMBER_CAST = auto(); STRING_CAST = auto(); BOOL_CAST = auto()
    EOF = auto()

TokenLiteralType = Union[float, str, bool, None]

class Token:
    def __init__(self, token_type: TokenType, lexeme: str, literal: TokenLiteralType, line: int):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __repr__(self) -> str:
        value = self.lexeme if self.token_type == TokenType.IDENTIFIER else self.literal
        return f"{self.token_type.name}: {value}" if value is not None else self.token_type.name

TokenKeywords = {
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
    "number": TokenType.NUMBER_CAST, 
    "string": TokenType.STRING_CAST, 
    "bool": TokenType.BOOL_CAST,
}