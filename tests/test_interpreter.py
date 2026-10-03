import io
import unittest
from contextlib import redirect_stdout

from rlangc.backends.interpreter import InterpreterError, execute
from rlangc.ir.ir import IRInstruction, IRModule
from rlangc.pipeline import run


class InterpreterTests(unittest.TestCase):
    def _run_and_capture(self, source: str) -> str:
        module = run(source)
        output = io.StringIO()
        with redirect_stdout(output):
            execute(module)
        return output.getvalue()

    def test_executes_arithmetic_and_builtin_print(self) -> None:
        output = self._run_and_capture("let x = 1\nx += 2\nprint(x)")
        self.assertEqual(output, "3\n")

    def test_executes_function_calls_and_returns(self) -> None:
        output = self._run_and_capture(
            "def add(x: int, y: int) -> int:\n"
            "    return x + y\n"
            "let result = add(2, 3)\n"
            "print(result)"
        )
        self.assertEqual(output, "5\n")

    def test_executes_for_loop_over_range(self) -> None:
        output = self._run_and_capture(
            "let total = 0\n"
            "for value in range(4):\n"
            "    total += value\n"
            "print(total)"
        )
        self.assertEqual(output, "6\n")

    def test_raises_for_const_reassignment(self) -> None:
        module = run("const value = 1")
        rewritten = IRModule(
            tokens=module.tokens,
            statement_count=module.statement_count,
            instructions=module.instructions
            + [
                IRInstruction(opcode="PUSH_CONST", operands=(2,)),
                IRInstruction(opcode="STORE_NAME", operands=("value", "assign")),
            ],
        )
        with self.assertRaisesRegex(InterpreterError, "Cannot reassign const 'value'"):
            execute(rewritten)


if __name__ == "__main__":
    unittest.main()
