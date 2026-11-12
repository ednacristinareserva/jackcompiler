
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lexer import Lexer
from compilation_engine import CompilationEngine


class TestCompilationEngine(unittest.TestCase):

    def compile_jack(self, source):
        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "Main.vm"
            tokens = Lexer(source).tokenize()
            CompilationEngine(tokens, output_path).compile_class()
            return output_path.read_text(encoding="utf-8").splitlines()

    def test_constante_e_retorno(self):
        source = """
        class Main {
            function int main() {
                return 7;
            }
        }
        """
        self.assertEqual(
            self.compile_jack(source),
            [
                "function Main.main 0",
                "push constant 7",
                "return",
            ],
        )

    def test_variaveis_locais(self):
        source = """
        class Main {
            function int main() {
                var int x, y;
                let x = 10;
                let y = x + 5;
                return y;
            }
        }
        """
        self.assertEqual(
            self.compile_jack(source),
            [
                "function Main.main 2",
                "push constant 10",
                "pop local 0",
                "push local 0",
                "push constant 5",
                "add",
                "pop local 1",
                "push local 1",
                "return",
            ],
        )

    def test_multiplicacao_e_divisao(self):
        source = """
        class Main {
            function int main() {
                return (6 * 3) / 2;
            }
        }
        """
        commands = self.compile_jack(source)
        self.assertIn("call Math.multiply 2", commands)
        self.assertIn("call Math.divide 2", commands)

    def test_operadores_unarios(self):
        source = """
        class Main {
            function int main() {
                return ~(-1);
            }
        }
        """
        commands = self.compile_jack(source)
        self.assertIn("neg", commands)
        self.assertIn("not", commands)

    def test_retorno_void(self):
        source = """
        class Main {
            function void main() {
                return;
            }
        }
        """
        self.assertEqual(
            self.compile_jack(source),
            [
                "function Main.main 0",
                "push constant 0",
                "return",
            ],
        )

    def test_if_else(self):
        source = """
        class Main {
            function int main() {
                if (true) {
                    return 1;
                } else {
                    return 0;
                }
            }
        }
        """
        commands = self.compile_jack(source)
        self.assertTrue(any(c.startswith("if-goto IF_TRUE") for c in commands))
        self.assertTrue(any(c.startswith("label IF_FALSE") for c in commands))
        self.assertTrue(any(c.startswith("label IF_END") for c in commands))

    def test_while(self):
        source = """
        class Main {
            function void main() {
                var int x;
                let x = 0;
                while (x < 3) {
                    let x = x + 1;
                }
                return;
            }
        }
        """
        commands = self.compile_jack(source)
        self.assertTrue(any(c.startswith("label WHILE_EXP") for c in commands))
        self.assertTrue(any(c.startswith("if-goto WHILE_END") for c in commands))
        self.assertIn("lt", commands)

    def test_chamada_de_funcao(self):
        source = """
        class Main {
            function void main() {
                do Output.printInt(7);
                return;
            }
        }
        """
        commands = self.compile_jack(source)
        self.assertIn("call Output.printInt 1", commands)
        self.assertIn("pop temp 0", commands)

    def test_construtor(self):
        source = """
        class Point {
            field int x, y;

            constructor Point new() {
                return this;
            }
        }
        """
        commands = self.compile_jack(source)
        self.assertIn("function Point.new 0", commands)
        self.assertIn("push constant 2", commands)
        self.assertIn("call Memory.alloc 1", commands)
        self.assertIn("pop pointer 0", commands)

    def test_metodo(self):
        source = """
        class Point {
            field int x;

            method int getX() {
                return x;
            }
        }
        """
        commands = self.compile_jack(source)
        self.assertIn("function Point.getX 0", commands)
        self.assertIn("push argument 0", commands)
        self.assertIn("pop pointer 0", commands)
        self.assertIn("push this 0", commands)

    def test_array(self):
        source = """
        class Main {
            function int main() {
                var Array a;
                let a = Array.new(2);
                let a[0] = 42;
                return a[0];
            }
        }
        """
        commands = self.compile_jack(source)
        self.assertIn("call Array.new 1", commands)
        self.assertIn("pop that 0", commands)
        self.assertIn("push that 0", commands)

    def test_string(self):
        source = """
        class Main {
            function void main() {
                do Output.printString("Hi");
                return;
            }
        }
        """
        commands = self.compile_jack(source)
        self.assertIn("push constant 2", commands)
        self.assertIn("call String.new 1", commands)
        self.assertEqual(commands.count("call String.appendChar 2"), 2)

    def test_variavel_nao_declarada(self):
        source = """
        class Main {
            function void main() {
                let x = 5;
                return;
            }
        }
        """
        with self.assertRaises(SyntaxError):
            self.compile_jack(source)


if __name__ == "__main__":
    unittest.main()
