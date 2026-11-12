
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from symbol_table import SymbolTable


class TestSymbolTable(unittest.TestCase):

    def setUp(self):
        self.table = SymbolTable()

    def test_define_static(self):
        self.table.define("contador", "int", "static")

        self.assertEqual(self.table.kind_of("contador"), "static")
        self.assertEqual(self.table.type_of("contador"), "int")
        self.assertEqual(self.table.index_of("contador"), 0)

    def test_define_field(self):
        self.table.define("x", "int", "field")
        self.table.define("y", "int", "field")

        self.assertEqual(self.table.index_of("x"), 0)
        self.assertEqual(self.table.index_of("y"), 1)
        self.assertEqual(self.table.var_count("field"), 2)

    def test_contadores_independentes(self):
        self.table.define("a", "int", "static")
        self.table.define("b", "int", "field")
        self.table.define("c", "int", "arg")
        self.table.define("d", "int", "var")

        self.assertEqual(self.table.index_of("a"), 0)
        self.assertEqual(self.table.index_of("b"), 0)
        self.assertEqual(self.table.index_of("c"), 0)
        self.assertEqual(self.table.index_of("d"), 0)

    def test_start_subroutine_limpa_escopo_local(self):
        self.table.define("x", "int", "field")
        self.table.define("parametro", "int", "arg")
        self.table.define("local", "boolean", "var")

        self.table.start_subroutine()

        self.assertIsNone(self.table.kind_of("parametro"))
        self.assertIsNone(self.table.kind_of("local"))
        self.assertEqual(self.table.kind_of("x"), "field")

        self.assertEqual(self.table.var_count("arg"), 0)
        self.assertEqual(self.table.var_count("var"), 0)

    def test_indices_reiniciam_na_nova_subrotina(self):
        self.table.define("a", "int", "arg")
        self.table.define("b", "int", "var")

        self.table.start_subroutine()

        self.table.define("novo_arg", "int", "arg")
        self.table.define("nova_var", "int", "var")

        self.assertEqual(self.table.index_of("novo_arg"), 0)
        self.assertEqual(self.table.index_of("nova_var"), 0)

    def test_escopo_local_tem_prioridade(self):
        self.table.define("valor", "int", "field")
        self.table.define("valor", "boolean", "var")

        self.assertEqual(self.table.kind_of("valor"), "var")
        self.assertEqual(self.table.type_of("valor"), "boolean")

        self.table.start_subroutine()

        self.assertEqual(self.table.kind_of("valor"), "field")
        self.assertEqual(self.table.type_of("valor"), "int")

    def test_simbolo_inexistente(self):
        self.assertIsNone(self.table.kind_of("inexistente"))
        self.assertIsNone(self.table.type_of("inexistente"))
        self.assertIsNone(self.table.index_of("inexistente"))

    def test_categoria_invalida(self):
        with self.assertRaises(ValueError):
            self.table.define("x", "int", "global")

        with self.assertRaises(ValueError):
            self.table.var_count("global")


if __name__ == "__main__":
    unittest.main()
