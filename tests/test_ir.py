import unittest

from rlangc.frontend.lexer import tokenize
from rlangc.frontend.parser import parse
from rlangc.ir.ir import from_ast


class IRTests(unittest.TestCase):
    def _opcodes(self, source: str):
        module = parse(tokenize(source))
        ir_module = from_ast(module)
        return [(instruction.opcode, instruction.operands) for instruction in ir_module.instructions]

    def test_generates_ir_for_let_and_assignment(self) -> None:
        instructions = self._opcodes("let x = 1\nx += 2")
        self.assertEqual(
            instructions,
            [
                ("PUSH_CONST", (1,)),
                ("STORE_NAME", ("x", "let")),
                ("LOAD_NAME", ("x",)),
                ("PUSH_CONST", (2,)),
                ("BINARY_OP", ("+",)),
                ("STORE_NAME", ("x", "assign")),
            ],
        )

    def test_generates_ir_for_if_else(self) -> None:
        instructions = self._opcodes("if true:\n    let x = 1\nelse:\n    let x = 2")
        self.assertEqual(
            instructions,
            [
                ("PUSH_CONST", (True,)),
                ("JUMP_IF_FALSE", ("if_else_1",)),
                ("PUSH_CONST", (1,)),
                ("STORE_NAME", ("x", "let")),
                ("JUMP", ("if_end_0",)),
                ("LABEL", ("if_else_1",)),
                ("PUSH_CONST", (2,)),
                ("STORE_NAME", ("x", "let")),
                ("LABEL", ("if_end_0",)),
            ],
        )

    def test_generates_ir_for_function_call(self) -> None:
        instructions = self._opcodes("def add(x, y):\n    return x + y\nlet sum = add(1, 2)")
        self.assertEqual(
            instructions,
            [
                ("FUNCTION_BEGIN", ("add", ("x", "y"), None, False)),
                ("LOAD_NAME", ("x",)),
                ("LOAD_NAME", ("y",)),
                ("BINARY_OP", ("+",)),
                ("RETURN", ()),
                ("FUNCTION_END", ("add",)),
                ("LOAD_NAME", ("add",)),
                ("PUSH_CONST", (1,)),
                ("PUSH_CONST", (2,)),
                ("CALL", (2,)),
                ("STORE_NAME", ("sum", "let")),
            ],
        )


if __name__ == "__main__":
    unittest.main()
