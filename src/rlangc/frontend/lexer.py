from typing import List

from rlangc.frontend.ast import Token


def tokenize(source: str) -> List[Token]:
    parts = source.split()
    return [Token(kind="WORD", value=part) for part in parts]
