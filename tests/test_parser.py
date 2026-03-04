import unittest

from rlangc.frontend.ast import BinaryExpression, Identifier, LetStatement, Literal, ReturnStatement
from rlangc.frontend.lexer import tokenize
from rlangc.frontend.parser import parse


class ParserTests(unittest.TestCase):
    def test_parse_let_statement_with_type_annotation(self) -> None:
        module = parse(tokenize("let count: int = 42"))
        self.assertEqual(len(module.statements), 1)
        stmt = module.statements[0]
        self.assertIsInstance(stmt, LetStatement)
        self.assertEqual(stmt.name, "count")
        self.assertEqual(stmt.annotation, "int")
        self.assertFalse(stmt.is_const)
        self.assertIsInstance(stmt.value, Literal)
        self.assertEqual(stmt.value.value, 42)

    def test_parse_const_expression_respects_precedence(self) -> None:
        module = parse(tokenize("const value = x + y * 2"))
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

    def test_parse_return_statement(self) -> None:
        module = parse(tokenize("return 1 + 2"))
        stmt = module.statements[0]
        self.assertIsInstance(stmt, ReturnStatement)
        self.assertIsNotNone(stmt.value)
        self.assertIsInstance(stmt.value, BinaryExpression)
        self.assertEqual(stmt.value.operator, "+")


if __name__ == "__main__":
    unittest.main()
