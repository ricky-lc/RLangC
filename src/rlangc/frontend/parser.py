from typing import List

from rlangc.frontend.ast import Module, Token


def parse(tokens: List[Token]) -> Module:
    return Module(tokens=tokens)
