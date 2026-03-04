from dataclasses import dataclass
from typing import List

from rlangc.frontend.ast import Module


@dataclass(frozen=True)
class IRModule:
    tokens: List[str]
    statement_count: int


def from_ast(module: Module) -> IRModule:
    return IRModule(tokens=[token.value for token in module.tokens], statement_count=len(module.statements))
