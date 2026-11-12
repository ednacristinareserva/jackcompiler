
"""Geração de código VM para programas Jack."""

from symbol_table import SymbolTable
from vm_writer import VMWriter


class CompilationEngine:
    """Compila tokens Jack em instruções VM."""

    TYPE_KEYWORDS = {"int", "char", "boolean"}
    CLASS_VAR_KEYWORDS = {"static", "field"}
    SUBROUTINE_KEYWORDS = {"constructor", "function", "method"}

    def __init__(self, tokens, output_path):
        self.tokens = list(tokens)
        self.position = 0
        self.symbol_table = SymbolTable()
        self.vm_writer = VMWriter(output_path)
        self.class_name = ""

    def peek(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def advance(self):
        token = self.peek()
        if token is None:
            raise SyntaxError("Fim inesperado do arquivo.")
        self.position += 1
        return token

    def consume(self, token_type, value=None):
        token = self.advance()

        if token[0] != token_type:
            raise SyntaxError(f"Esperado {token_type}, recebido {token}.")

        if value is not None and token[1] != value:
            raise SyntaxError(f"Esperado {value}, recebido {token[1]}.")

        return token[1]

    def match(self, token_type, value=None):
        token = self.peek()
        return (
            token is not None
            and token[0] == token_type
            and (value is None or token[1] == value)
        )

    def compile_class(self):
        self.consume("keyword", "class")
        self.class_name = self.consume("identifier")
        self.consume("symbol", "{")

        while (
            self.match("keyword")
            and self.peek()[1] in self.CLASS_VAR_KEYWORDS
        ):
            self.compile_class_var_dec()

        while (
            self.match("keyword")
            and self.peek()[1] in self.SUBROUTINE_KEYWORDS
        ):
            self.compile_subroutine()

        self.consume("symbol", "}")

        if self.peek() is not None:
            raise SyntaxError("Tokens inesperados após o fim da classe.")

        self.vm_writer.close()

    def compile_type(self, allow_void=False):
        token = self.peek()
        valid = self.TYPE_KEYWORDS | ({"void"} if allow_void else set())

        if token and (
            (token[0] == "keyword" and token[1] in valid)
            or token[0] == "identifier"
        ):
            return self.advance()[1]

        raise SyntaxError("Tipo inválido.")

    def compile_class_var_dec(self):
        kind = self.consume("keyword")
        type_ = self.compile_type()

        name = self.consume("identifier")
        self.symbol_table.define(name, type_, kind)

        while self.match("symbol", ","):
            self.consume("symbol", ",")
            name = self.consume("identifier")
            self.symbol_table.define(name, type_, kind)

        self.consume("symbol", ";")

    def compile_subroutine(self):
        kind = self.consume("keyword")
        self.symbol_table.start_subroutine()

        self.compile_type(allow_void=True)
        name = self.consume("identifier")

        if kind == "method":
            self.symbol_table.define("this", self.class_name, "arg")

        self.consume("symbol", "(")
        self.compile_parameter_list()
        self.consume("symbol", ")")

        self.compile_subroutine_body(name, kind)

    def compile_parameter_list(self):
        if self.match("symbol", ")"):
            return

        while True:
            type_ = self.compile_type()
            name = self.consume("identifier")
            self.symbol_table.define(name, type_, "arg")

            if not self.match("symbol", ","):
                break

            self.consume("symbol", ",")

    def compile_subroutine_body(self, name, kind):
        self.consume("symbol", "{")

        while self.match("keyword", "var"):
            self.compile_var_dec()

        full_name = f"{self.class_name}.{name}"
        n_locals = self.symbol_table.var_count("var")
        self.vm_writer.write_function(full_name, n_locals)

        if kind == "constructor":
            n_fields = self.symbol_table.var_count("field")
            self.vm_writer.write_push("constant", n_fields)
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("pointer", 0)

        elif kind == "method":
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop("pointer", 0)

        self.compile_statements()
        self.consume("symbol", "}")

    def compile_var_dec(self):
        self.consume("keyword", "var")
        type_ = self.compile_type()

        name = self.consume("identifier")
        self.symbol_table.define(name, type_, "var")

        while self.match("symbol", ","):
            self.consume("symbol", ",")
            name = self.consume("identifier")
            self.symbol_table.define(name, type_, "var")

        self.consume("symbol", ";")

    def compile_statements(self):
        raise NotImplementedError(
            "A compilação de comandos será implementada na próxima etapa."
        )
