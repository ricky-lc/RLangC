import unittest

from rlangc.frontend.ast import (
    AssignmentStatement,
    BinaryExpression,
    CallExpression,
    DictLiteral,
    ForStatement,
    FunctionDefinition,
    Identifier,
    IfStatement,
    KeywordArgument,
    ImportStatement,
    LetStatement,
    Literal,
    ReturnStatement,
    UnaryExpression,
    WhileStatement,
)
from rlangc.frontend.lexer import tokenize
from rlangc.frontend.parser import parse


class ParserTests(unittest.TestCase):
    def test_parse_function_with_typed_parameters_and_return(self) -> None:
        source = "def add(x: int, y: int = 2) -> int:\n    return x + y\n"
        module = parse(tokenize(source))
        self.assertEqual(len(module.statements), 1)
        func = module.statements[0]
        self.assertIsInstance(func, FunctionDefinition)
        self.assertEqual(func.name, "add")
        self.assertEqual(len(func.parameters), 2)
        self.assertEqual(func.parameters[0].name, "x")
        self.assertEqual(func.parameters[0].annotation, "int")
        self.assertEqual(func.return_annotation, "int")
        self.assertEqual(len(func.body), 1)
        self.assertIsInstance(func.body[0], ReturnStatement)

    def test_parse_if_elif_else_with_indentation(self) -> None:
        source = (
            "if score >= 90:\n"
            "    let grade = \"A\"\n"
            "elif score >= 80:\n"
            "    let grade = \"B\"\n"
            "else:\n"
            "    let grade = \"C\"\n"
        )
        module = parse(tokenize(source))
        self.assertEqual(len(module.statements), 1)
        stmt = module.statements[0]
        self.assertIsInstance(stmt, IfStatement)
        self.assertEqual(len(stmt.body), 1)
        self.assertEqual(len(stmt.elif_branches), 1)
        self.assertIsNotNone(stmt.else_body)
        self.assertEqual(len(stmt.else_body), 1)

    def test_parse_while_and_assignment(self) -> None:
        source = "while i < 3:\n    i = i + 1\n"
        module = parse(tokenize(source))
        self.assertEqual(len(module.statements), 1)
        stmt = module.statements[0]
        self.assertIsInstance(stmt, WhileStatement)
        self.assertEqual(len(stmt.body), 1)
        self.assertIsInstance(stmt.body[0], AssignmentStatement)
        assignment = stmt.body[0]
        self.assertEqual(assignment.operator, "=")

    def test_parse_for_loop_with_brace_style(self) -> None:
        source = "for item in numbers { print(item) }"
        module = parse(tokenize(source))
        self.assertEqual(len(module.statements), 1)
        stmt = module.statements[0]
        self.assertIsInstance(stmt, ForStatement)
        self.assertEqual(stmt.variable, "item")
        self.assertEqual(len(stmt.body), 1)
        call_stmt = stmt.body[0]
        self.assertTrue(hasattr(call_stmt, "expression"))
        self.assertIsInstance(call_stmt.expression, CallExpression)

    def test_parse_expression_respects_precedence(self) -> None:
        module = parse(tokenize("const value = x + y * 2"))
        self.assertEqual(len(module.statements), 1)
        stmt = module.statements[0]
        self.assertIsInstance(stmt, LetStatement)
        self.assertTrue(stmt.is_const)
        expr = stmt.value
        self.assertIsInstance(expr, BinaryExpression)
        self.assertEqual(expr.operator, "+")
        self.assertIsInstance(expr.left, Identifier)
        self.assertEqual(expr.left.name, "x")
        self.assertIsInstance(expr.right, BinaryExpression)
        self.assertEqual(expr.right.operator, "*")
        self.assertIsInstance(expr.right.right, Literal)
        self.assertEqual(expr.right.right.value, 2)

    def test_parse_unary_bitwise_not(self) -> None:
        module = parse(tokenize("let inverted = ~mask"))
        self.assertEqual(len(module.statements), 1)
        stmt = module.statements[0]
        self.assertIsInstance(stmt, LetStatement)
        self.assertEqual(stmt.name, "inverted")
        self.assertIsInstance(stmt.value, UnaryExpression)
        self.assertEqual(stmt.value.operator, "~")
        self.assertIsInstance(stmt.value.operand, Identifier)
        self.assertEqual(stmt.value.operand.name, "mask")

    def test_parse_import_with_alias(self) -> None:
        module = parse(tokenize("import net.http as http"))
        self.assertEqual(len(module.statements), 1)
        stmt = module.statements[0]
        self.assertIsInstance(stmt, ImportStatement)
        self.assertEqual(stmt.module, "net.http")
        self.assertEqual(stmt.alias, "http")

    def test_parse_async_function_and_await_expression(self) -> None:
        source = "async def fetch(url):\n    return await http.get(url)\n"
        module = parse(tokenize(source))
        self.assertEqual(len(module.statements), 1)
        stmt = module.statements[0]
        self.assertIsInstance(stmt, FunctionDefinition)
        self.assertTrue(stmt.is_async)
        self.assertIsInstance(stmt.body[0], ReturnStatement)
        self.assertIsInstance(stmt.body[0].value, UnaryExpression)
        self.assertEqual(stmt.body[0].value.operator, "await")

    def test_parse_call_with_keyword_argument(self) -> None:
        module = parse(tokenize('print(str(1), end="")'))
        self.assertEqual(len(module.statements), 1)
        stmt = module.statements[0]
        self.assertTrue(hasattr(stmt, "expression"))
        call = stmt.expression
        self.assertIsInstance(call, CallExpression)
        self.assertEqual(len(call.arguments), 2)
        self.assertIsInstance(call.arguments[1], KeywordArgument)
        self.assertEqual(call.arguments[1].name, "end")

    def test_parse_multiline_dictionary_literal(self) -> None:
        source = 'let data = {\n    "x": 1,\n    "y": 2\n}\n'
        module = parse(tokenize(source))
        self.assertEqual(len(module.statements), 1)
        stmt = module.statements[0]
        self.assertIsInstance(stmt, LetStatement)
        self.assertIsInstance(stmt.value, DictLiteral)
        self.assertEqual(len(stmt.value.entries), 2)


if __name__ == "__main__":
    unittest.main()
