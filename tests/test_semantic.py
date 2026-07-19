import unittest

from rlangc.frontend.lexer import tokenize
from rlangc.frontend.parser import parse
from rlangc.frontend.semantic import SemanticError, analyze


class SemanticTests(unittest.TestCase):
    def test_detects_undefined_variable(self) -> None:
        module = parse(tokenize("let x = y + 1"))
        with self.assertRaisesRegex(SemanticError, "Undefined variable 'y'"):
            analyze(module)

    def test_detects_const_reassignment(self) -> None:
        module = parse(tokenize("const value = 1\nvalue = 2"))
        with self.assertRaisesRegex(SemanticError, "Cannot reassign const 'value'"):
            analyze(module)

    def test_scope_isolated_from_if_block(self) -> None:
        module = parse(tokenize("if true:\n    let scoped = 1\nprint(scoped)"))
        with self.assertRaisesRegex(SemanticError, "Undefined variable 'scoped'"):
            analyze(module)

    def test_type_annotation_mismatch_is_reported(self) -> None:
        module = parse(tokenize('let count: int = "one"'))
        with self.assertRaisesRegex(SemanticError, "Incompatible value type for 'count'"):
            analyze(module)

    def test_builtin_names_are_available(self) -> None:
        module = parse(tokenize("print(len([1, 2, 3]))"))
        analyze(module)


if __name__ == "__main__":
    unittest.main()
