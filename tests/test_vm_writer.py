
import sys
import unittest
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vm_writer import VMWriter


class TestVMWriter(unittest.TestCase):

    def test_write_push(self):
        writer = VMWriter("output.vm")
        writer.write_push("constant", 5)
        self.assertEqual(writer.commands, ["push constant 5"])

    def test_write_pop(self):
        writer = VMWriter("output.vm")
        writer.write_pop("local", 2)
        self.assertEqual(writer.commands, ["pop local 2"])

    def test_write_arithmetic(self):
        writer = VMWriter("output.vm")
        writer.write_arithmetic("add")
        writer.write_arithmetic("sub")
        self.assertEqual(writer.commands, ["add", "sub"])

    def test_arithmetic_invalido(self):
        writer = VMWriter("output.vm")
        with self.assertRaises(ValueError):
            writer.write_arithmetic("multiply")

    def test_write_label(self):
        writer = VMWriter("output.vm")
        writer.write_label("LOOP_START")
        self.assertEqual(writer.commands, ["label LOOP_START"])

    def test_write_goto(self):
        writer = VMWriter("output.vm")
        writer.write_goto("LOOP_START")
        self.assertEqual(writer.commands, ["goto LOOP_START"])

    def test_write_if(self):
        writer = VMWriter("output.vm")
        writer.write_if("IF_TRUE")
        self.assertEqual(writer.commands, ["if-goto IF_TRUE"])

    def test_write_call(self):
        writer = VMWriter("output.vm")
        writer.write_call("Math.multiply", 2)
        self.assertEqual(writer.commands, ["call Math.multiply 2"])

    def test_write_function(self):
        writer = VMWriter("output.vm")
        writer.write_function("Main.main", 0)
        self.assertEqual(writer.commands, ["function Main.main 0"])

    def test_write_return(self):
        writer = VMWriter("output.vm")
        writer.write_return()
        self.assertEqual(writer.commands, ["return"])

    def test_close_grava_arquivo(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "Main.vm"

            writer = VMWriter(output_path)
            writer.write_function("Main.main", 0)
            writer.write_push("constant", 7)
            writer.write_return()
            writer.close()

            conteudo = output_path.read_text(encoding="utf-8")

            esperado = (
                "function Main.main 0\n"
                "push constant 7\n"
                "return\n"
            )

            self.assertEqual(conteudo, esperado)


if __name__ == "__main__":
    unittest.main()
