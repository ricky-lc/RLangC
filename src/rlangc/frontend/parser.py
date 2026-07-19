from typing import List, Optional, Tuple

from rlangc.frontend.ast import (
    AssignmentStatement,
    AttributeExpression,
    BinaryExpression,
    CallExpression,
    Expression,
    ExpressionStatement,
    ForStatement,
    FunctionDefinition,
    Identifier,
    IfStatement,
    IndexExpression,
    ListLiteral,
    LetStatement,
    Literal,
    Module,
    Parameter,
    ReturnStatement,
    Statement,
    Token,
    UnaryExpression,
    WhileStatement,
    DictLiteral,
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
    _ASSIGNMENT_OPERATORS = {"=", "+=", "-=", "*=", "/=", "%="}

    def __init__(self, tokens: List[Token]) -> None:
        self._tokens = tokens
        self._index = 0

    def parse_module(self) -> Module:
        statements: List[Statement] = []
        self._consume_newlines()
        while not self._is_at_end():
            statements.append(self._parse_statement())
            self._consume_newlines()
        return Module(tokens=self._tokens, statements=statements)

    def _parse_statement(self) -> Statement:
        token = self._peek()
        if token.kind == "KEYWORD":
            if token.value in {"let", "const"}:
                return self._parse_let_statement()
            if token.value == "return":
                return self._parse_return_statement()
            if token.value == "def":
                return self._parse_function_definition()
            if token.value == "if":
                return self._parse_if_statement()
            if token.value == "while":
                return self._parse_while_statement()
            if token.value == "for":
                return self._parse_for_statement()

        expr = self._parse_expression()
        if self._is_assignment_operator(self._peek_optional()):
            operator = self._advance().value
            value = self._parse_expression()
            return AssignmentStatement(target=expr, operator=operator, value=value)
        return ExpressionStatement(expression=expr)

    def _parse_let_statement(self) -> LetStatement:
        keyword = self._advance()
        is_const = keyword.value == "const"
        name_token = self._expect("IDENTIFIER", "Expected identifier after binding keyword")
        annotation = None
        if self._match("PUNCT", ":"):
            annotation = self._parse_type_name("Expected type annotation after ':'")
        self._expect("OPERATOR", "Expected '=' after binding name", expected_value="=")
        value = self._parse_expression()
        return LetStatement(name=name_token.value, value=value, is_const=is_const, annotation=annotation)

    def _parse_return_statement(self) -> ReturnStatement:
        self._advance()
        if self._is_at_end():
            return ReturnStatement(value=None)
        next_token = self._peek()
        if next_token.kind in {"NEWLINE", "DEDENT"} or (next_token.kind == "PUNCT" and next_token.value == "}"):
            return ReturnStatement(value=None)
        return ReturnStatement(value=self._parse_expression())

    def _parse_function_definition(self) -> FunctionDefinition:
        self._advance()
        name = self._expect("IDENTIFIER", "Expected function name after 'def'").value
        self._expect("PUNCT", "Expected '(' after function name", expected_value="(")
        parameters = self._parse_parameters()
        self._expect("PUNCT", "Expected ')' after parameter list", expected_value=")")
        return_annotation = None
        if self._match("OPERATOR", "-"):
            self._expect("OPERATOR", "Expected '->' return type annotation", expected_value=">")
            return_annotation = self._parse_type_name("Expected return type name after '->'")
        body = self._parse_block()
        return FunctionDefinition(
            name=name,
            parameters=parameters,
            return_annotation=return_annotation,
            body=body,
        )

    def _parse_parameters(self) -> List[Parameter]:
        parameters: List[Parameter] = []
        if self._check("PUNCT", ")"):
            return parameters
        while True:
            param_name = self._expect("IDENTIFIER", "Expected parameter name").value
            annotation = None
            default = None
            if self._match("PUNCT", ":"):
                annotation = self._parse_type_name("Expected parameter type after ':'")
            if self._match("OPERATOR", "="):
                default = self._parse_expression()
            parameters.append(Parameter(name=param_name, annotation=annotation, default=default))
            if not self._match("PUNCT", ","):
                break
        return parameters

    def _parse_if_statement(self) -> IfStatement:
        self._advance()
        condition = self._parse_expression()
        body = self._parse_block()
        elif_branches: List[Tuple[Expression, List[Statement]]] = []
        while self._match("KEYWORD", "elif"):
            elif_condition = self._parse_expression()
            elif_body = self._parse_block()
            elif_branches.append((elif_condition, elif_body))
        else_body = None
        if self._match("KEYWORD", "else"):
            else_body = self._parse_block()
        return IfStatement(condition=condition, body=body, elif_branches=elif_branches, else_body=else_body)

    def _parse_while_statement(self) -> WhileStatement:
        self._advance()
        condition = self._parse_expression()
        body = self._parse_block()
        return WhileStatement(condition=condition, body=body)

    def _parse_for_statement(self) -> ForStatement:
        self._advance()
        variable = self._expect("IDENTIFIER", "Expected loop variable after 'for'").value
        self._expect("KEYWORD", "Expected 'in' in for loop", expected_value="in")
        iterable = self._parse_expression()
        body = self._parse_block()
        return ForStatement(variable=variable, iterable=iterable, body=body)

    def _parse_block(self) -> List[Statement]:
        if self._match("PUNCT", "{"):
            brace_statements: List[Statement] = []
            self._consume_newlines()
            while not self._match("PUNCT", "}"):
                if self._is_at_end():
                    raise ParseError("Unterminated brace block")
                brace_statements.append(self._parse_statement())
                self._consume_newlines()
            return brace_statements

        self._expect("PUNCT", "Expected block opener ':' or '{'", expected_value=":")
        if self._match("NEWLINE"):
            self._expect("INDENT", "Expected indented block after ':'")
            indent_statements: List[Statement] = []
            self._consume_newlines()
            while not self._match("DEDENT"):
                if self._is_at_end():
                    raise ParseError("Unterminated indented block")
                indent_statements.append(self._parse_statement())
                self._consume_newlines()
            return indent_statements
        return [self._parse_statement()]

    def _parse_expression(self, min_precedence: int = 1) -> Expression:
        left = self._parse_unary()
        while True:
            token = self._peek_optional()
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
        if token.kind == "OPERATOR" and token.value in {"+", "-", "~"}:
            self._advance()
            return UnaryExpression(operator=token.value, operand=self._parse_unary())
        if token.kind == "KEYWORD" and token.value == "not":
            self._advance()
            return UnaryExpression(operator="not", operand=self._parse_unary())
        return self._parse_postfix()

    def _parse_postfix(self) -> Expression:
        expr = self._parse_primary()
        while True:
            if self._match("PUNCT", "("):
                args: List[Expression] = []
                if not self._check("PUNCT", ")"):
                    while True:
                        args.append(self._parse_expression())
                        if not self._match("PUNCT", ","):
                            break
                self._expect("PUNCT", "Expected ')' after function arguments", expected_value=")")
                expr = CallExpression(callee=expr, arguments=args)
                continue
            if self._match("PUNCT", "["):
                index = self._parse_expression()
                self._expect("PUNCT", "Expected ']' after index expression", expected_value="]")
                expr = IndexExpression(target=expr, index=index)
                continue
            if self._match("PUNCT", "."):
                name = self._expect("IDENTIFIER", "Expected attribute name after '.'").value
                expr = AttributeExpression(target=expr, name=name)
                continue
            break
        return expr

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
        if token.kind == "PUNCT" and token.value == "[":
            self._advance()
            elements: List[Expression] = []
            if not self._check("PUNCT", "]"):
                while True:
                    elements.append(self._parse_expression())
                    if not self._match("PUNCT", ","):
                        break
            self._expect("PUNCT", "Expected ']' after list literal", expected_value="]")
            return ListLiteral(elements=elements)
        if token.kind == "PUNCT" and token.value == "{":
            self._advance()
            entries: List[Tuple[Expression, Expression]] = []
            if not self._check("PUNCT", "}"):
                while True:
                    key = self._parse_expression()
                    self._expect("PUNCT", "Expected ':' in dictionary literal", expected_value=":")
                    value = self._parse_expression()
                    entries.append((key, value))
                    if not self._match("PUNCT", ","):
                        break
            self._expect("PUNCT", "Expected '}' after dictionary literal", expected_value="}")
            return DictLiteral(entries=entries)
        raise ParseError(f"Unexpected token: {token.kind} {token.value!r}")

    def _binary_operator(self, token: Optional[Token]) -> Optional[str]:
        if token is None:
            return None
        if token.kind == "OPERATOR" and token.value in self._BINARY_PRECEDENCE:
            return token.value
        if token.kind == "KEYWORD" and token.value in {"and", "or"}:
            return token.value
        return None

    def _parse_type_name(self, message: str) -> str:
        token = self._peek()
        if token.kind == "IDENTIFIER":
            return self._advance().value
        if token.kind == "KEYWORD" and token.value == "none":
            return self._advance().value
        raise ParseError(message)

    def _consume_newlines(self) -> None:
        while self._match("NEWLINE"):
            continue

    def _check(self, kind: str, value: Optional[str] = None) -> bool:
        token = self._peek_optional()
        if token is None or token.kind != kind:
            return False
        if value is not None and token.value != value:
            return False
        return True

    def _is_assignment_operator(self, token: Optional[Token]) -> bool:
        return token is not None and token.kind == "OPERATOR" and token.value in self._ASSIGNMENT_OPERATORS

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
        token = self._peek_optional()
        if token is None:
            raise ParseError("Unexpected end of input")
        return token

    def _peek_optional(self) -> Optional[Token]:
        if self._is_at_end():
            return None
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
        if not self._check(kind, value):
            return False
        self._index += 1
        return True

    def _is_at_end(self) -> bool:
        return self._index >= len(self._tokens)


def parse(tokens: List[Token]) -> Module:
    return _Parser(tokens).parse_module()
