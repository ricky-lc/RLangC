from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass(frozen=True)
class Token:
    kind: str
    value: str


@dataclass(frozen=True)
class Expression:
    pass


@dataclass(frozen=True)
class Identifier(Expression):
    name: str


@dataclass(frozen=True)
class Literal(Expression):
    value: Any


@dataclass(frozen=True)
class UnaryExpression(Expression):
    operator: str
    operand: Expression


@dataclass(frozen=True)
class BinaryExpression(Expression):
    left: Expression
    operator: str
    right: Expression


@dataclass(frozen=True)
class Statement:
    pass


@dataclass(frozen=True)
class LetStatement(Statement):
    name: str
    value: Expression
    is_const: bool
    annotation: Optional[str] = None


@dataclass(frozen=True)
class ReturnStatement(Statement):
    value: Optional[Expression]


@dataclass(frozen=True)
class ExpressionStatement(Statement):
    expression: Expression


@dataclass(frozen=True)
class Module:
    tokens: List[Token]
    statements: List[Statement]
