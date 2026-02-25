from rlangc.frontend import lexer, parser
from rlangc.ir import ir


def run(source: str) -> ir.IRModule:
    tokens = lexer.tokenize(source)
    module = parser.parse(tokens)
    return ir.from_ast(module)
