from typing import List, Optional

from rlangc.frontend.ast import (
    BinaryExpression,
    Expression,
    ExpressionStatement,
    Identifier,
    LetStatement,
    Literal,
    Module,
    ReturnStatement,
    Statement,
    Token,
    UnaryExpression,
)


class ParseError(ValueError):
    pass


class _Parser:
    _BINARY_PRECEDENCE = {
        "or": 1,
        "and": 2,
        "==": 3,
        "!=": 3,
        "<": 4,
        "<=": 4,
        ">": 4,
        ">=": 4,
        "+": 5,
        "-": 5,
        "*": 6,
        "/": 6,
        "%": 6,
        "//": 6,
        "**": 7,
    }

    def __init__(self, tokens: List[Token]) -> None:
        self._tokens = tokens
        self._index = 0

    def parse_module(self) -> Module:
        statements = []
        while not self._is_at_end():
            statements.append(self._parse_statement())
        return Module(tokens=self._tokens, statements=statements)

    def _parse_statement(self) -> Statement:
        token = self._peek()
        if token.kind == "KEYWORD" and token.value in {"let", "const"}:
            return self._parse_let_statement()
        if token.kind == "KEYWORD" and token.value == "return":
            return self._parse_return_statement()
        return ExpressionStatement(expression=self._parse_expression())

    def _parse_let_statement(self) -> LetStatement:
        keyword = self._advance()
        is_const = keyword.value == "const"
        name_token = self._expect("IDENTIFIER", "Expected identifier after binding keyword")
        annotation = None
        if self._match("PUNCT", ":"):
            annotation = self._expect("IDENTIFIER", "Expected type annotation after ':'").value
        self._expect("OPERATOR", "Expected '=' after binding name", expected_value="=")
        value = self._parse_expression()
        return LetStatement(name=name_token.value, value=value, is_const=is_const, annotation=annotation)

    def _parse_return_statement(self) -> ReturnStatement:
        self._advance()  # return keyword
        if self._is_at_end():
            return ReturnStatement(value=None)
        return ReturnStatement(value=self._parse_expression())

    def _parse_expression(self, min_precedence: int = 1) -> Expression:
        left = self._parse_unary()
        while True:
            if self._is_at_end():
                break
            token = self._peek()
            operator = self._binary_operator(token)
            if operator is None:
                break
            precedence = self._BINARY_PRECEDENCE[operator]
            if precedence < min_precedence:
                break
            self._advance()
            next_min = precedence if self._is_right_associative(operator) else precedence + 1
            right = self._parse_expression(next_min)
            left = BinaryExpression(left=left, operator=operator, right=right)
        return left

    def _parse_unary(self) -> Expression:
        token = self._peek()
        if token.kind == "OPERATOR" and token.value in {"+", "-"}:
            self._advance()
            return UnaryExpression(operator=token.value, operand=self._parse_unary())
        if token.kind == "KEYWORD" and token.value == "not":
            self._advance()
            return UnaryExpression(operator="not", operand=self._parse_unary())
        return self._parse_primary()

    def _parse_primary(self) -> Expression:
        token = self._peek()
        if token.kind == "INTEGER":
            self._advance()
            return Literal(value=int(token.value))
        if token.kind == "FLOAT":
            self._advance()
            return Literal(value=float(token.value))
        if token.kind == "STRING":
            self._advance()
            return Literal(value=self._extract_string_literal(token))
        if token.kind == "IDENTIFIER":
            self._advance()
            return Identifier(name=token.value)
        if token.kind == "KEYWORD" and token.value in {"true", "false", "none"}:
            self._advance()
            if token.value == "true":
                return Literal(value=True)
            if token.value == "false":
                return Literal(value=False)
            return Literal(value=None)
        if token.kind == "PUNCT" and token.value == "(":
            self._advance()
            expression = self._parse_expression()
            self._expect("PUNCT", "Expected ')' after grouped expression", expected_value=")")
            return expression
        raise ParseError(f"Unexpected token: {token.kind} {token.value!r}")

    def _binary_operator(self, token: Token) -> Optional[str]:
        if token.kind == "OPERATOR" and token.value in self._BINARY_PRECEDENCE:
            return token.value
        if token.kind == "KEYWORD" and token.value in {"and", "or"}:
            return token.value
        return None

    def _is_right_associative(self, operator: str) -> bool:
        return operator == "**"

    def _extract_string_literal(self, token: Token) -> str:
        if len(token.value) < 2:
            raise ParseError("Invalid string literal token")
        quote = token.value[0]
        if quote not in {'"', "'"} or token.value[-1] != quote:
            raise ParseError("Invalid string literal token")
        return token.value[1:-1]

    def _peek(self) -> Token:
        if self._is_at_end():
            raise ParseError("Unexpected end of input")
        return self._tokens[self._index]

    def _advance(self) -> Token:
        token = self._peek()
        self._index += 1
        return token

    def _expect(self, kind: str, message: str, expected_value: Optional[str] = None) -> Token:
        token = self._peek()
        if token.kind != kind:
            raise ParseError(message)
        if expected_value is not None and token.value != expected_value:
            raise ParseError(message)
        return self._advance()

    def _match(self, kind: str, value: Optional[str] = None) -> bool:
        if self._is_at_end():
            return False
        token = self._tokens[self._index]
        if token.kind != kind:
            return False
        if value is not None and token.value != value:
            return False
        self._index += 1
        return True

    def _is_at_end(self) -> bool:
        return self._index >= len(self._tokens)


def parse(tokens: List[Token]) -> Module:
    return _Parser(tokens).parse_module()
