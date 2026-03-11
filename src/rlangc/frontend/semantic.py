from dataclasses import dataclass
from typing import Dict, List, Optional

from rlangc.frontend.ast import (
    AssignmentStatement,
    AttributeExpression,
    BinaryExpression,
    CallExpression,
    DictLiteral,
    Expression,
    ExpressionStatement,
    ForStatement,
    FunctionDefinition,
    Identifier,
    IfStatement,
    IndexExpression,
    LetStatement,
    ListLiteral,
    Literal,
    Module,
    ReturnStatement,
    Statement,
    UnaryExpression,
    WhileStatement,
)


class SemanticError(ValueError):
    pass


@dataclass(frozen=True)
class Symbol:
    name: str
    is_const: bool
    type_name: Optional[str]


class _Scope:
    def __init__(self, parent: Optional["_Scope"] = None) -> None:
        self._parent = parent
        self._symbols: Dict[str, Symbol] = {}

    def define(self, symbol: Symbol) -> None:
        self._symbols[symbol.name] = symbol

    def resolve(self, name: str) -> Optional[Symbol]:
        if name in self._symbols:
            return self._symbols[name]
        if self._parent is not None:
            return self._parent.resolve(name)
        return None


class _SemanticAnalyzer:
    _BUILTINS = {
        "assert": Symbol(name="assert", is_const=True, type_name="function"),
        "defer": Symbol(name="defer", is_const=True, type_name="function"),
        "format": Symbol(name="format", is_const=True, type_name="function"),
        "len": Symbol(name="len", is_const=True, type_name="function"),
        "print": Symbol(name="print", is_const=True, type_name="function"),
        "range": Symbol(name="range", is_const=True, type_name="function"),
        "type": Symbol(name="type", is_const=True, type_name="function"),
    }
    _NUMERIC_TYPES = {"int", "float"}

    def __init__(self) -> None:
        self._scope = _Scope()
        self._return_types: List[Optional[str]] = []
        for symbol in self._BUILTINS.values():
            self._scope.define(symbol)

    def analyze_module(self, module: Module) -> Module:
        self._analyze_statements(module.statements, create_scope=False)
        return module

    def _analyze_statements(self, statements: List[Statement], create_scope: bool = True) -> None:
        previous_scope = self._scope
        if create_scope:
            self._scope = _Scope(parent=previous_scope)
        try:
            for statement in statements:
                self._analyze_statement(statement)
        finally:
            if create_scope:
                self._scope = previous_scope

    def _analyze_statement(self, statement: Statement) -> None:
        if isinstance(statement, LetStatement):
            value_type = self._analyze_expression(statement.value)
            symbol_type = statement.annotation or value_type
            if statement.annotation is not None and not self._is_assignable(statement.annotation, value_type):
                raise SemanticError(
                    f"Cannot assign value of type {value_type!r} to {statement.name!r} annotated as {statement.annotation!r}"
                )
            self._scope.define(Symbol(name=statement.name, is_const=statement.is_const, type_name=symbol_type))
            return

        if isinstance(statement, AssignmentStatement):
            value_type = self._analyze_expression(statement.value)
            if isinstance(statement.target, Identifier):
                symbol = self._require_symbol(statement.target.name)
                if symbol.is_const:
                    raise SemanticError(f"Cannot reassign const binding {statement.target.name!r}")
                if statement.operator == "=" and not self._is_assignable(symbol.type_name, value_type):
                    raise SemanticError(
                        f"Cannot assign value of type {value_type!r} to {statement.target.name!r} of type {symbol.type_name!r}"
                    )
            else:
                self._analyze_expression(statement.target)
            return

        if isinstance(statement, ExpressionStatement):
            self._analyze_expression(statement.expression)
            return

        if isinstance(statement, ReturnStatement):
            value_type = "none"
            if statement.value is not None:
                value_type = self._analyze_expression(statement.value)
            current_return_type = self._current_return_type()
            if current_return_type is not None and not self._is_assignable(current_return_type, value_type):
                raise SemanticError(
                    f"Cannot return value of type {value_type!r} from function declared as {current_return_type!r}"
                )
            return

        if isinstance(statement, FunctionDefinition):
            self._scope.define(Symbol(name=statement.name, is_const=True, type_name="function"))
            for parameter in statement.parameters:
                if parameter.default is not None:
                    self._analyze_expression(parameter.default)
            previous_scope = self._scope
            self._scope = _Scope(parent=previous_scope)
            self._return_types.append(statement.return_annotation)
            try:
                for parameter in statement.parameters:
                    self._scope.define(Symbol(name=parameter.name, is_const=False, type_name=parameter.annotation))
                self._analyze_statements(statement.body, create_scope=False)
            finally:
                self._return_types.pop()
                self._scope = previous_scope
            return

        if isinstance(statement, IfStatement):
            self._analyze_expression(statement.condition)
            self._analyze_statements(statement.body)
            for condition, body in statement.elif_branches:
                self._analyze_expression(condition)
                self._analyze_statements(body)
            if statement.else_body is not None:
                self._analyze_statements(statement.else_body)
            return

        if isinstance(statement, WhileStatement):
            self._analyze_expression(statement.condition)
            self._analyze_statements(statement.body)
            return

        if isinstance(statement, ForStatement):
            self._analyze_expression(statement.iterable)
            previous_scope = self._scope
            self._scope = _Scope(parent=previous_scope)
            try:
                self._scope.define(Symbol(name=statement.variable, is_const=False, type_name=None))
                self._analyze_statements(statement.body, create_scope=False)
            finally:
                self._scope = previous_scope
            return

        raise SemanticError(f"Unsupported statement for semantic analysis: {type(statement).__name__}")

    def _analyze_expression(self, expression: Expression) -> Optional[str]:
        if isinstance(expression, Identifier):
            return self._require_symbol(expression.name).type_name

        if isinstance(expression, Literal):
            return self._infer_literal_type(expression.value)

        if isinstance(expression, UnaryExpression):
            return self._analyze_expression(expression.operand)

        if isinstance(expression, BinaryExpression):
            left_type = self._analyze_expression(expression.left)
            right_type = self._analyze_expression(expression.right)
            return self._infer_binary_type(expression.operator, left_type, right_type)

        if isinstance(expression, CallExpression):
            self._analyze_expression(expression.callee)
            for argument in expression.arguments:
                self._analyze_expression(argument)
            return None

        if isinstance(expression, IndexExpression):
            self._analyze_expression(expression.target)
            self._analyze_expression(expression.index)
            return None

        if isinstance(expression, AttributeExpression):
            self._analyze_expression(expression.target)
            return None

        if isinstance(expression, ListLiteral):
            for element in expression.elements:
                self._analyze_expression(element)
            return "list"

        if isinstance(expression, DictLiteral):
            for key, value in expression.entries:
                self._analyze_expression(key)
                self._analyze_expression(value)
            return "dict"

        raise SemanticError(f"Unsupported expression for semantic analysis: {type(expression).__name__}")

    def _require_symbol(self, name: str) -> Symbol:
        symbol = self._scope.resolve(name)
        if symbol is None:
            raise SemanticError(f"Undefined variable {name!r}")
        return symbol

    def _current_return_type(self) -> Optional[str]:
        if not self._return_types:
            return None
        return self._return_types[-1]

    def _infer_literal_type(self, value: object) -> str:
        if value is None:
            return "none"
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, int):
            return "int"
        if isinstance(value, float):
            return "float"
        if isinstance(value, str):
            return "str"
        return "any"

    def _infer_binary_type(self, operator: str, left_type: Optional[str], right_type: Optional[str]) -> Optional[str]:
        if operator in {"and", "or", "==", "!=", "<", "<=", ">", ">="}:
            return "bool"
        if operator == "+" and left_type == right_type == "str":
            return "str"
        if left_type in self._NUMERIC_TYPES and right_type in self._NUMERIC_TYPES:
            if "float" in {left_type, right_type} or operator == "/":
                return "float"
            return "int"
        if left_type is None or right_type is None:
            return None
        if operator == "+" and left_type == right_type == "list":
            return "list"
        raise SemanticError(
            f"Unsupported operand types in binary expression for {operator!r}: {left_type!r} and {right_type!r}"
        )

    def _is_assignable(self, expected: Optional[str], actual: Optional[str]) -> bool:
        if expected in {None, "any"} or actual in {None, "any"}:
            return True
        if expected == actual:
            return True
        return expected == "float" and actual == "int"


def analyze(module: Module) -> Module:
    return _SemanticAnalyzer().analyze_module(module)
