import re
from typing import List

from rlangc.frontend.ast import Token

_TAB_WIDTH = 4


def tokenize(source: str) -> List[Token]:
    tokens: List[Token] = []
    indent_stack = [0]
    brace_depth = 0
    lines = source.splitlines()

    for line_number, raw_line in enumerate(lines, start=1):
        stripped_line = raw_line.lstrip(" \t")
        if not stripped_line or stripped_line.startswith("#"):
            continue

        leading_whitespace = raw_line[: len(raw_line) - len(stripped_line)]
        indent_width = _indent_width(leading_whitespace)
        if brace_depth == 0:
            if indent_width > indent_stack[-1]:
                indent_stack.append(indent_width)
                tokens.append(Token(kind="INDENT", value="INDENT"))
            else:
                while indent_width < indent_stack[-1]:
                    indent_stack.pop()
                    tokens.append(Token(kind="DEDENT", value="DEDENT"))
                if indent_width != indent_stack[-1]:
                    raise ValueError(f"Inconsistent indentation at line {line_number}")

        offset = len(raw_line) - len(stripped_line)
        index = 0
        while index < len(stripped_line):
            match = _TOKEN_RE.match(stripped_line, index)
            if match is None:
                column = offset + index + 1
                raise ValueError(f"Unexpected character {stripped_line[index]!r} at line {line_number}, column {column}")
            kind = match.lastgroup
            value = match.group()
            index = match.end()

            if kind in {"WHITESPACE"}:
                continue
            if kind == "COMMENT":
                break
            if kind == "IDENTIFIER" and value in _KEYWORDS:
                token = Token(kind="KEYWORD", value=value)
            elif kind == "MISMATCH":
                column = offset + match.start() + 1
                raise ValueError(f"Unexpected character {value!r} at line {line_number}, column {column}")
            else:
                token = Token(kind=kind, value=value)
            tokens.append(token)
            if token.kind == "PUNCT" and token.value == "{":
                brace_depth += 1
            elif token.kind == "PUNCT" and token.value == "}":
                brace_depth -= 1
                if brace_depth < 0:
                    raise ValueError(f"Unexpected '}}' at line {line_number}")

        tokens.append(Token(kind="NEWLINE", value="\n"))

    if brace_depth != 0:
        raise ValueError("Unterminated brace block")

    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token(kind="DEDENT", value="DEDENT"))

    return tokens


def _indent_width(prefix: str) -> int:
    width = 0
    for char in prefix:
        if char == " ":
            width += 1
        elif char == "\t":
            width += _TAB_WIDTH
        else:
            break
    return width


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
    "async",
    "await",
}

_TOKEN_RE = re.compile(
    r"""
    (?P<WHITESPACE>[ \t]+)
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
