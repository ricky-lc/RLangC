from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Token:
    kind: str
    value: str


@dataclass(frozen=True)
class Module:
    tokens: List[Token]
