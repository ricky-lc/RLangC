import unittest

from rlangc.frontend.lexer import tokenize


class LexerTests(unittest.TestCase):
    def test_tokenize_keywords_numbers_and_symbols(self) -> None:
        source = 'let x = 3.14\nif x >= 1 { print("ok") }'
        tokens = tokenize(source)
        self.assertEqual(
            [(token.kind, token.value) for token in tokens],
            [
                ("KEYWORD", "let"),
                ("IDENTIFIER", "x"),
                ("OPERATOR", "="),
                ("FLOAT", "3.14"),
                ("NEWLINE", "\n"),
                ("KEYWORD", "if"),
                ("IDENTIFIER", "x"),
                ("OPERATOR", ">="),
                ("INTEGER", "1"),
                ("PUNCT", "{"),
                ("IDENTIFIER", "print"),
                ("PUNCT", "("),
                ("STRING", '"ok"'),
                ("PUNCT", ")"),
                ("PUNCT", "}"),
                ("NEWLINE", "\n"),
            ],
        )

    def test_tokenize_emits_indent_and_dedent(self) -> None:
        source = "if true:\n    let x = 1\nlet y = 2\n"
        tokens = tokenize(source)
        self.assertEqual(
            [token.kind for token in tokens],
            [
                "KEYWORD",
                "KEYWORD",
                "PUNCT",
                "NEWLINE",
                "INDENT",
                "KEYWORD",
                "IDENTIFIER",
                "OPERATOR",
                "INTEGER",
                "NEWLINE",
                "DEDENT",
                "KEYWORD",
                "IDENTIFIER",
                "OPERATOR",
                "INTEGER",
                "NEWLINE",
            ],
        )

    def test_tokenize_skips_comments(self) -> None:
        source = "const y = 2 # trailing comment"
        tokens = tokenize(source)
        self.assertEqual([token.value for token in tokens], ["const", "y", "=", "2", "\n"])

    def test_tokenize_raises_on_invalid_character(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unexpected character"):
            tokenize("let x = 1 €")

    def test_tokenize_reports_error_location(self) -> None:
        with self.assertRaisesRegex(ValueError, "line 2, column 1"):
            tokenize("let x = 1\n€")

    def test_tokenize_supports_all_defined_operator_tokens(self) -> None:
        source = "a ** b // c == d != e <= f >= g << h >> i += j -= k *= l /= m %= n + o - p * q / r % s = t < u > v & w | x ^ y ~z"
        tokens = tokenize(source)
        operators = [token.value for token in tokens if token.kind == "OPERATOR"]
        self.assertEqual(
            operators,
            [
                "**",
                "//",
                "==",
                "!=",
                "<=",
                ">=",
                "<<",
                ">>",
                "+=",
                "-=",
                "*=",
                "/=",
                "%=",
                "+",
                "-",
                "*",
                "/",
                "%",
                "=",
                "<",
                ">",
                "&",
                "|",
                "^",
                "~",
            ],
        )

    def test_tokenize_handles_tab_indentation(self) -> None:
        source = "if true:\n\tlet x = 1\nlet y = 2\n"
        tokens = tokenize(source)
        self.assertEqual(tokens[4].kind, "INDENT")
        self.assertEqual(tokens[10].kind, "DEDENT")

    def test_tokenize_raises_on_inconsistent_indentation(self) -> None:
        source = "if true:\n    let x = 1\n  let y = 2\n"
        with self.assertRaisesRegex(ValueError, "Inconsistent indentation at line 3"):
            tokenize(source)

    def test_tokenize_raises_on_unterminated_brace_block(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unterminated brace block"):
            tokenize("if true {\n    let x = 1\n")

    def test_tokenize_raises_on_unexpected_closing_brace(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unexpected '\\}' at line 1"):
            tokenize("}")


if __name__ == "__main__":
    unittest.main()
