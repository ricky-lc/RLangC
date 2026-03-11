import unittest

from rlangc.frontend.semantic import SemanticError
from rlangc import pipeline


class SemanticAnalysisTests(unittest.TestCase):
    def test_pipeline_rejects_undefined_variable(self) -> None:
        with self.assertRaisesRegex(SemanticError, "Undefined variable 'count'"):
            pipeline.run("let total = count + 1")

    def test_pipeline_rejects_const_reassignment(self) -> None:
        source = "const max_size = 10\nmax_size = 20\n"
        with self.assertRaisesRegex(SemanticError, "Cannot reassign const binding 'max_size'"):
            pipeline.run(source)

    def test_pipeline_rejects_annotation_mismatch(self) -> None:
        with self.assertRaisesRegex(SemanticError, "annotated as 'int'"):
            pipeline.run('let count: int = "hello"')

    def test_pipeline_allows_shadowing_and_builtins(self) -> None:
        source = (
            "let value = 1\n"
            "if true:\n"
            "    let value = value + 1\n"
            "print(value)\n"
        )
        module = pipeline.run(source)
        self.assertEqual(module.statement_count, 3)


if __name__ == "__main__":
    unittest.main()
