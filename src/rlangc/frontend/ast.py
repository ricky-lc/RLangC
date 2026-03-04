from dataclasses import dataclass
from typing import Any, List, Optional, Tuple


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
class CallExpression(Expression):
    callee: Expression
    arguments: List[Expression]


@dataclass(frozen=True)
class IndexExpression(Expression):
    target: Expression
    index: Expression


@dataclass(frozen=True)
class AttributeExpression(Expression):
    target: Expression
    name: str


@dataclass(frozen=True)
class ListLiteral(Expression):
    elements: List[Expression]


@dataclass(frozen=True)
class DictLiteral(Expression):
    entries: List[Tuple[Expression, Expression]]


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
class AssignmentStatement(Statement):
    target: Expression
    operator: str
    value: Expression


@dataclass(frozen=True)
class Parameter:
    name: str
    annotation: Optional[str] = None
    default: Optional[Expression] = None


@dataclass(frozen=True)
class FunctionDefinition(Statement):
    name: str
    parameters: List[Parameter]
    return_annotation: Optional[str]
    body: List[Statement]


@dataclass(frozen=True)
class IfStatement(Statement):
    condition: Expression
    body: List[Statement]
    elif_branches: List[Tuple[Expression, List[Statement]]]
    else_body: Optional[List[Statement]]


@dataclass(frozen=True)
class WhileStatement(Statement):
    condition: Expression
    body: List[Statement]


@dataclass(frozen=True)
class ForStatement(Statement):
    variable: str
    iterable: Expression
    body: List[Statement]


@dataclass(frozen=True)
class Module:
    tokens: List[Token]
    statements: List[Statement]
