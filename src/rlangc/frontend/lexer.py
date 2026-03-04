import re
from typing import List

from rlangc.frontend.ast import Token


def tokenize(source: str) -> List[Token]:
    tokens: List[Token] = []
    append = tokens.append
    for match in _TOKEN_RE.finditer(source):
        kind = match.lastgroup
        value = match.group()
        if kind in {"WHITESPACE", "NEWLINE", "COMMENT"}:
            continue
        if kind == "IDENTIFIER" and value in _KEYWORDS:
            append(Token(kind="KEYWORD", value=value))
            continue
        if kind == "MISMATCH":
            raise ValueError(f"Unexpected character: {value!r}")
        append(Token(kind=kind, value=value))
    return tokens


_KEYWORDS = {
    "def",
    "let",
    "const",
    "if",
    "elif",
    "else",
    "while",
    "for",
    "in",
    "return",
    "and",
    "or",
    "not",
    "true",
    "false",
    "none",
    "import",
    "as",
}

_TOKEN_RE = re.compile(
    r"""
    (?P<WHITESPACE>[ \t]+)
  | (?P<NEWLINE>\r?\n)
  | (?P<COMMENT>\#.*)
  | (?P<STRING>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')
  | (?P<FLOAT>\d+\.\d+)
  | (?P<INTEGER>\d+)
  | (?P<OPERATOR>\*\*|//|==|!=|<=|>=|<<|>>|\+=|-=|\*=|/=|%=|[+\-*/%=<>&|^~])
  | (?P<PUNCT>[(){}\[\],.:])
  | (?P<IDENTIFIER>[A-Za-z_][A-Za-z0-9_]*)
  | (?P<MISMATCH>.)
    """,
    re.VERBOSE,
)
