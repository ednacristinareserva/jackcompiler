
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lexer import Lexer
from parser import Parser, ParserError


class TestParser(unittest.TestCase):

    def parse_source(self, source):
        return Parser(Lexer(source).tokenize()).parse()

    def test_classe_minima(self):
        xml = self.parse_source("class Empty { }")
        self.assertIn("<class>", xml)
        self.assertIn("<identifier> Empty </identifier>", xml)
        self.assertTrue(xml.rstrip().endswith("</class>"))

    def test_declaracoes_e_expressoes(self):
        xml = self.parse_source(
            "class A { function int f(int x) { var int y; "
            "let y = x + 2; return y; } }"
        )
        self.assertIn("<subroutineDec>", xml)
        self.assertIn("<varDec>", xml)
        self.assertIn("<letStatement>", xml)
        self.assertIn("<returnStatement>", xml)
        self.assertIn("<expression>", xml)

    def test_array_e_chamada_de_funcao(self):
        xml = self.parse_source(
            "class A { function void f() { var Array a; "
            "let a[1] = 3; do Output.printInt(a[1]); return; } }"
        )
        self.assertIn("<expressionList>", xml)
        self.assertIn("<doStatement>", xml)

    def test_escape_xml(self):
        xml = self.parse_source(
            "class A { function boolean f(int x) { return x < 3; } }"
        )
        self.assertIn("&lt;", xml)

    def test_sintaxe_invalida(self):
        with self.assertRaises(ParserError):
            self.parse_source("class A { function void f( { return; } }")


if __name__ == "__main__":
    unittest.main()
