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
            ],
        )

    def test_tokenize_skips_comments(self) -> None:
        source = "const y = 2 # trailing comment"
        tokens = tokenize(source)
        self.assertEqual([token.value for token in tokens], ["const", "y", "=", "2"])

    def test_tokenize_raises_on_invalid_character(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unexpected character"):
            tokenize("let x = 1 €")


if __name__ == "__main__":
    unittest.main()
