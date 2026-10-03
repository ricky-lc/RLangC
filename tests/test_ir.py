import unittest

from rlangc.frontend.lexer import tokenize
from rlangc.frontend.parser import parse
from rlangc.ir.ir import IRInstruction, IRModule, build_cfg, from_ast, optimize


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

    def test_build_cfg_tracks_branch_successors(self) -> None:
        module = from_ast(parse(tokenize("let x = 0\nif x < 2:\n    x += 1\nelse:\n    x += 2\nprint(x)")))
        cfg = build_cfg(module)
        self.assertGreaterEqual(len(cfg.blocks), 3)
        branch_blocks = [
            block for block in cfg.blocks if block.instructions[-1].opcode in {"JUMP_IF_FALSE", "FOR_ITER"}
        ]
        self.assertTrue(branch_blocks)
        self.assertEqual(len(branch_blocks[0].successors), 2)

    def test_optimize_folds_constants_and_removes_redundant_jumps(self) -> None:
        module = IRModule(
            tokens=[],
            statement_count=0,
            instructions=[
                IRInstruction("PUSH_CONST", (2,)),
                IRInstruction("PUSH_CONST", (3,)),
                IRInstruction("BINARY_OP", ("+",)),
                IRInstruction("JUMP", ("end",)),
                IRInstruction("LABEL", ("end",)),
            ],
        )
        optimized = optimize(module)
        self.assertEqual(
            [(instruction.opcode, instruction.operands) for instruction in optimized.instructions],
            [("PUSH_CONST", (5,)), ("LABEL", ("end",))],
        )


if __name__ == "__main__":
    unittest.main()
