
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from lexer import Lexer


class TestLexer(unittest.TestCase):

    def test_keywords(self):
        source = "class function return"
        tokens = Lexer(source).tokenize()

        self.assertEqual(
            tokens,
            [
                ("keyword", "class"),
                ("keyword", "function"),
                ("keyword", "return"),
            ],
        )

    def test_symbols(self):
        source = "{ } ( ) ; = +"
        tokens = Lexer(source).tokenize()

        self.assertEqual(
            tokens,
            [
                ("symbol", "{"),
                ("symbol", "}"),
                ("symbol", "("),
                ("symbol", ")"),
                ("symbol", ";"),
                ("symbol", "="),
                ("symbol", "+"),
            ],
        )

    def test_integer_constant(self):
        source = "0 123 32767"
        tokens = Lexer(source).tokenize()

        self.assertEqual(
            tokens,
            [
                ("integerConstant", "0"),
                ("integerConstant", "123"),
                ("integerConstant", "32767"),
            ],
        )

    def test_string_constant(self):
        source = '"Ola Jack"'
        tokens = Lexer(source).tokenize()

        self.assertEqual(
            tokens,
            [("stringConstant", "Ola Jack")],
        )

    def test_identifier(self):
        source = "Main numero minhaVariavel"
        tokens = Lexer(source).tokenize()

        self.assertEqual(
            tokens,
            [
                ("identifier", "Main"),
                ("identifier", "numero"),
                ("identifier", "minhaVariavel"),
            ],
        )

    def test_ignores_line_comment(self):
        source = "class // comentario\nreturn"
        tokens = Lexer(source).tokenize()

        self.assertEqual(
            tokens,
            [
                ("keyword", "class"),
                ("keyword", "return"),
            ],
        )

    def test_ignores_block_comment(self):
        source = "class /* comentario */ return"
        tokens = Lexer(source).tokenize()

        self.assertEqual(
            tokens,
            [
                ("keyword", "class"),
                ("keyword", "return"),
            ],
        )

    def test_comment_markers_inside_string(self):
        source = '"Texto // e /* teste */"'
        tokens = Lexer(source).tokenize()

        self.assertEqual(
            tokens,
            [("stringConstant", "Texto // e /* teste */")],
        )

    def test_unclosed_string(self):
        source = '"string sem fechamento'

        with self.assertRaises(ValueError):
            Lexer(source).tokenize()

    def test_unclosed_block_comment(self):
        source = "class /* comentario sem fechamento"

        with self.assertRaises(ValueError):
            Lexer(source).tokenize()

    def test_integer_out_of_range(self):
        source = "32768"

        with self.assertRaises(ValueError):
            Lexer(source).tokenize()

    def test_invalid_character(self):
        source = "@"

        with self.assertRaises(ValueError):
            Lexer(source).tokenize()


    def test_tokens_without_spaces(self):
        source = "let x=10;"
        tokens = Lexer(source).tokenize()

        self.assertEqual(
            tokens,
            [
                ("keyword", "let"),
                ("identifier", "x"),
                ("symbol", "="),
                ("integerConstant", "10"),
                ("symbol", ";"),
            ],
        )

    def test_ignores_different_whitespace(self):
        source = "class\tMain {\nreturn;\n}"
        tokens = Lexer(source).tokenize()

        self.assertEqual(
            tokens,
            [
                ("keyword", "class"),
                ("identifier", "Main"),
                ("symbol", "{"),
                ("keyword", "return"),
                ("symbol", ";"),
                ("symbol", "}"),
            ],
        )

    def test_identifier_with_underscore_and_numbers(self):
        source = "minha_variavel2"
        tokens = Lexer(source).tokenize()

        self.assertEqual(
            tokens,
            [("identifier", "minha_variavel2")],
        )

if __name__ == "__main__":
    unittest.main()
