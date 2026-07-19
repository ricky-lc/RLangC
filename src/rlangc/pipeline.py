from rlangc.frontend import lexer, parser, semantic
from rlangc.ir import ir


def run(source: str) -> ir.IRModule:
    tokens = lexer.tokenize(source)
    module = parser.parse(tokens)
    semantic.analyze(module)
    return ir.from_ast(module)
