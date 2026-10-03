from dataclasses import dataclass
from typing import Any, List, Tuple

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
    ImportStatement,
    IndexExpression,
    KeywordArgument,
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


@dataclass(frozen=True)
class IRInstruction:
    opcode: str
    operands: Tuple[Any, ...] = ()


@dataclass(frozen=True)
class IRModule:
    tokens: List[str]
    statement_count: int
    instructions: List[IRInstruction]


class _IRBuilder:
    def __init__(self) -> None:
        self.instructions: List[IRInstruction] = []
        self._label_counter = 0

    def emit(self, opcode: str, *operands: Any) -> None:
        self.instructions.append(IRInstruction(opcode=opcode, operands=operands))

    def new_label(self, prefix: str) -> str:
        label = f"{prefix}_{self._label_counter}"
        self._label_counter += 1
        return label

    def build_module(self, module: Module) -> IRModule:
        for statement in module.statements:
            self.compile_statement(statement)
        return IRModule(
            tokens=[token.value for token in module.tokens],
            statement_count=len(module.statements),
            instructions=self.instructions,
        )

    def compile_statement(self, statement: Statement) -> None:
        if isinstance(statement, LetStatement):
            self.compile_expression(statement.value)
            self.emit("STORE_NAME", statement.name, "const" if statement.is_const else "let")
            return
        if isinstance(statement, AssignmentStatement):
            self.compile_assignment(statement)
            return
        if isinstance(statement, ExpressionStatement):
            self.compile_expression(statement.expression)
            self.emit("POP")
            return
        if isinstance(statement, ReturnStatement):
            if statement.value is None:
                self.emit("PUSH_CONST", None)
            else:
                self.compile_expression(statement.value)
            self.emit("RETURN")
            return
        if isinstance(statement, IfStatement):
            self.compile_if(statement)
            return
        if isinstance(statement, WhileStatement):
            self.compile_while(statement)
            return
        if isinstance(statement, ForStatement):
            self.compile_for(statement)
            return
        if isinstance(statement, FunctionDefinition):
            self.compile_function(statement)
            return
        if isinstance(statement, ImportStatement):
            self.emit("IMPORT", statement.module, statement.alias or statement.module)
            return
        if isinstance(statement, ClassDefinition):
            self.emit("CLASS_BEGIN", statement.name, tuple(statement.bases))
            for class_statement in statement.body:
                self.compile_statement(class_statement)
            self.emit("CLASS_END", statement.name)
            return
        raise ValueError(f"Unsupported statement type for IR generation: {type(statement).__name__}")

    def compile_assignment(self, statement: AssignmentStatement) -> None:
        if not isinstance(statement.target, Identifier):
            self.compile_expression(statement.value)
            self.emit("ASSIGN_TARGET")
            return
        if statement.operator != "=":
            self.emit("LOAD_NAME", statement.target.name)
            self.compile_expression(statement.value)
            self.emit("BINARY_OP", statement.operator[:-1])
        else:
            self.compile_expression(statement.value)
        self.emit("STORE_NAME", statement.target.name, "assign")

    def compile_if(self, statement: IfStatement) -> None:
        end_label = self.new_label("if_end")
        next_label = self.new_label("if_else")
        self.compile_expression(statement.condition)
        self.emit("JUMP_IF_FALSE", next_label)
        for body_statement in statement.body:
            self.compile_statement(body_statement)
        self.emit("JUMP", end_label)
        self.emit("LABEL", next_label)

        for elif_condition, elif_body in statement.elif_branches:
            elif_next_label = self.new_label("if_elif")
            self.compile_expression(elif_condition)
            self.emit("JUMP_IF_FALSE", elif_next_label)
            for elif_statement in elif_body:
                self.compile_statement(elif_statement)
            self.emit("JUMP", end_label)
            self.emit("LABEL", elif_next_label)

        if statement.else_body is not None:
            for else_statement in statement.else_body:
                self.compile_statement(else_statement)
        self.emit("LABEL", end_label)

    def compile_while(self, statement: WhileStatement) -> None:
        start_label = self.new_label("while_start")
        end_label = self.new_label("while_end")
        self.emit("LABEL", start_label)
        self.compile_expression(statement.condition)
        self.emit("JUMP_IF_FALSE", end_label)
        for body_statement in statement.body:
            self.compile_statement(body_statement)
        self.emit("JUMP", start_label)
        self.emit("LABEL", end_label)

    def compile_for(self, statement: ForStatement) -> None:
        loop_label = self.new_label("for_loop")
        end_label = self.new_label("for_end")
        self.compile_expression(statement.iterable)
        self.emit("GET_ITER")
        self.emit("LABEL", loop_label)
        self.emit("FOR_ITER", statement.variable, end_label)
        for body_statement in statement.body:
            self.compile_statement(body_statement)
        self.emit("JUMP", loop_label)
        self.emit("LABEL", end_label)

    def compile_function(self, statement: FunctionDefinition) -> None:
        self.emit(
            "FUNCTION_BEGIN",
            statement.name,
            tuple(parameter.name for parameter in statement.parameters),
            statement.return_annotation,
            statement.is_async,
        )
        for body_statement in statement.body:
            self.compile_statement(body_statement)
        if not statement.body or not isinstance(statement.body[-1], ReturnStatement):
            self.emit("PUSH_CONST", None)
            self.emit("RETURN")
        self.emit("FUNCTION_END", statement.name)

    def compile_expression(self, expression: Expression) -> None:
        if isinstance(expression, Literal):
            self.emit("PUSH_CONST", expression.value)
            return
        if isinstance(expression, Identifier):
            self.emit("LOAD_NAME", expression.name)
            return
        if isinstance(expression, UnaryExpression):
            self.compile_expression(expression.operand)
            self.emit("UNARY_OP", expression.operator)
            return
        if isinstance(expression, BinaryExpression):
            self.compile_expression(expression.left)
            self.compile_expression(expression.right)
            self.emit("BINARY_OP", expression.operator)
            return
        if isinstance(expression, CallExpression):
            self.compile_expression(expression.callee)
            for argument in expression.arguments:
                if isinstance(argument, (NamedArgument, KeywordArgument)):
                    self.compile_expression(argument.value)
                    self.emit("KW_ARG", argument.name)
                else:
                    self.compile_expression(argument)
            self.emit("CALL", len(expression.arguments))
            return
        if isinstance(expression, ListLiteral):
            for element in expression.elements:
                self.compile_expression(element)
            self.emit("MAKE_LIST", len(expression.elements))
            return
        if isinstance(expression, DictLiteral):
            for key, value in expression.entries:
                self.compile_expression(key)
                self.compile_expression(value)
            self.emit("MAKE_DICT", len(expression.entries))
            return
        if isinstance(expression, IndexExpression):
            self.compile_expression(expression.target)
            self.compile_expression(expression.index)
            self.emit("INDEX_GET")
            return
        if isinstance(expression, AttributeExpression):
            self.compile_expression(expression.target)
            self.emit("LOAD_ATTR", expression.name)
            return
        if isinstance(expression, NamedArgument):
            self.compile_expression(expression.value)
            self.emit("KW_ARG", expression.name)
            return
        raise ValueError(f"Unsupported expression type for IR generation: {type(expression).__name__}")


def from_ast(module: Module) -> IRModule:
    return _IRBuilder().build_module(module)
