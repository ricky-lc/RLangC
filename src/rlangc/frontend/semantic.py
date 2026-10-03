from dataclasses import dataclass
from typing import Dict, List, Optional

from rlangc.frontend.ast import (
    AssignmentStatement,
    AttributeExpression,
    BinaryExpression,
    CallExpression,
    ClassDefinition,
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
    NamedArgument,
    ReturnStatement,
    Statement,
    UnaryExpression,
    WhileStatement,
)


class SemanticError(ValueError):
    pass


@dataclass
class Symbol:
    name: str
    is_const: bool
    annotation: Optional[str] = None


class Scope:
    def __init__(self, parent: Optional["Scope"] = None) -> None:
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}

    def define(self, symbol: Symbol) -> None:
        self.symbols[symbol.name] = symbol

    def resolve(self, name: str) -> Optional[Symbol]:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent is not None:
            return self.parent.resolve(name)
        return None


class _Analyzer:
    _BUILTINS = {
        "print",
        "len",
        "str",
        "int",
        "float",
        "bool",
        "list",
        "dict",
        "format",
        "range",
    }
    _COMPARISON_OPERATORS = {"==", "!=", "<", "<=", ">", ">="}

    def __init__(self) -> None:
        self._scope = Scope()
        for name in self._BUILTINS:
            self._scope.define(Symbol(name=name, is_const=True))

    def analyze(self, module: Module) -> None:
        self._analyze_statements(module.statements)

    def _analyze_statements(self, statements: List[Statement]) -> None:
        for statement in statements:
            self._analyze_statement(statement)

    def _analyze_statement(self, statement: Statement) -> None:
        if isinstance(statement, LetStatement):
            self._analyze_expression(statement.value)
            inferred_type = self._infer_expression_type(statement.value)
            if not self._is_type_compatible(statement.annotation, inferred_type):
                self._error(
                    f"Incompatible value type for '{statement.name}': "
                    f"expected {statement.annotation}, got {inferred_type}"
                )
            self._scope.define(
                Symbol(
                    name=statement.name,
                    is_const=statement.is_const,
                    annotation=statement.annotation or inferred_type,
                )
            )
            return

        if isinstance(statement, AssignmentStatement):
            self._analyze_expression(statement.value)
            target = statement.target
            if isinstance(target, Identifier):
                symbol = self._scope.resolve(target.name)
                if symbol is None:
                    if statement.operator != "=":
                        self._error(f"Undefined variable '{target.name}'")
                    self._scope.define(
                        Symbol(
                            name=target.name,
                            is_const=False,
                            annotation=self._infer_expression_type(statement.value),
                        )
                    )
                    return
                if symbol.is_const:
                    self._error(f"Cannot reassign const '{target.name}'")
                inferred_type = self._infer_expression_type(statement.value)
                if not self._is_type_compatible(symbol.annotation, inferred_type):
                    self._error(
                        f"Incompatible assignment type for '{target.name}': "
                        f"expected {symbol.annotation}, got {inferred_type}"
                    )
                if symbol.annotation is None:
                    symbol.annotation = inferred_type
                return
            self._analyze_expression(target)
            return

        if isinstance(statement, FunctionDefinition):
            self._scope.define(Symbol(name=statement.name, is_const=True, annotation="function"))
            for parameter in statement.parameters:
                if parameter.default is not None:
                    self._analyze_expression(parameter.default)
            with self._new_scope():
                for parameter in statement.parameters:
                    self._scope.define(
                        Symbol(name=parameter.name, is_const=False, annotation=parameter.annotation)
                    )
                self._analyze_statements(statement.body)
            return

        if isinstance(statement, ClassDefinition):
            self._scope.define(Symbol(name=statement.name, is_const=True, annotation="class"))
            for base_name in statement.bases:
                if self._scope.resolve(base_name) is None:
                    self._error(f"Undefined base class '{base_name}'")
            with self._new_scope():
                self._analyze_statements(statement.body)
            return

        if isinstance(statement, IfStatement):
            self._analyze_expression(statement.condition)
            with self._new_scope():
                self._analyze_statements(statement.body)
            for elif_condition, elif_body in statement.elif_branches:
                self._analyze_expression(elif_condition)
                with self._new_scope():
                    self._analyze_statements(elif_body)
            if statement.else_body is not None:
                with self._new_scope():
                    self._analyze_statements(statement.else_body)
            return

        if isinstance(statement, WhileStatement):
            self._analyze_expression(statement.condition)
            with self._new_scope():
                self._analyze_statements(statement.body)
            return

        if isinstance(statement, ForStatement):
            self._analyze_expression(statement.iterable)
            with self._new_scope():
                self._scope.define(Symbol(name=statement.variable, is_const=False))
                self._analyze_statements(statement.body)
            return

        if isinstance(statement, ReturnStatement):
            if statement.value is not None:
                self._analyze_expression(statement.value)
            return

        if isinstance(statement, ExpressionStatement):
            self._analyze_expression(statement.expression)
            return

    def _analyze_expression(self, expression: Expression) -> None:
        if isinstance(expression, Identifier):
            if self._scope.resolve(expression.name) is None:
                self._error(f"Undefined variable '{expression.name}'")
            return
        if isinstance(expression, Literal):
            return
        if isinstance(expression, UnaryExpression):
            self._analyze_expression(expression.operand)
            return
        if isinstance(expression, BinaryExpression):
            self._analyze_expression(expression.left)
            self._analyze_expression(expression.right)
            return
        if isinstance(expression, CallExpression):
            self._analyze_expression(expression.callee)
            for argument in expression.arguments:
                self._analyze_expression(argument)
            return
        if isinstance(expression, NamedArgument):
            self._analyze_expression(expression.value)
            return
        if isinstance(expression, ListLiteral):
            for element in expression.elements:
                self._analyze_expression(element)
            return
        if isinstance(expression, DictLiteral):
            for key, value in expression.entries:
                self._analyze_expression(key)
                self._analyze_expression(value)
            return
        if isinstance(expression, IndexExpression):
            self._analyze_expression(expression.target)
            self._analyze_expression(expression.index)
            return
        if isinstance(expression, AttributeExpression):
            self._analyze_expression(expression.target)
            return

    def _infer_expression_type(self, expression: Expression) -> Optional[str]:
        if isinstance(expression, Literal):
            if expression.value is None:
                return "none"
            if isinstance(expression.value, bool):
                return "bool"
            if isinstance(expression.value, int):
                return "int"
            if isinstance(expression.value, float):
                return "float"
            if isinstance(expression.value, str):
                return "str"
            return None
        if isinstance(expression, ListLiteral):
            return "list"
        if isinstance(expression, DictLiteral):
            return "dict"
        if isinstance(expression, Identifier):
            symbol = self._scope.resolve(expression.name)
            return None if symbol is None else symbol.annotation
        if isinstance(expression, UnaryExpression):
            if expression.operator == "not":
                return "bool"
            return self._infer_expression_type(expression.operand)
        if isinstance(expression, BinaryExpression):
            if expression.operator in self._COMPARISON_OPERATORS:
                return "bool"
            if expression.operator in {"and", "or"}:
                return "bool"
            left_type = self._infer_expression_type(expression.left)
            right_type = self._infer_expression_type(expression.right)
            if left_type is None or right_type is None:
                return None
            if left_type == right_type:
                return left_type
            if {left_type, right_type} == {"int", "float"}:
                return "float"
            return None
        return None

    def _is_type_compatible(self, expected: Optional[str], actual: Optional[str]) -> bool:
        if expected is None or actual is None:
            return True
        if expected == actual:
            return True
        if expected == "float" and actual == "int":
            return True
        return False

    def _new_scope(self) -> "_ScopeContext":
        return _ScopeContext(self)

    def _error(self, message: str) -> None:
        raise SemanticError(message)


class _ScopeContext:
    def __init__(self, analyzer: _Analyzer) -> None:
        self._analyzer = analyzer
        self._previous_scope: Optional[Scope] = None

    def __enter__(self) -> None:
        self._previous_scope = self._analyzer._scope
        self._analyzer._scope = Scope(parent=self._previous_scope)

    def __exit__(self, exc_type, exc, tb) -> None:
        assert self._previous_scope is not None
        self._analyzer._scope = self._previous_scope


def analyze(module: Module) -> None:
    _Analyzer().analyze(module)
