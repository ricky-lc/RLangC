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

    def test_tokenize_recognizes_async_await_keywords(self) -> None:
        tokens = tokenize("async def fetch():\n    return await call()\n")
        keyword_values = [token.value for token in tokens if token.kind == "KEYWORD"]
        self.assertIn("async", keyword_values)
        self.assertIn("await", keyword_values)


if __name__ == "__main__":
    unittest.main()
