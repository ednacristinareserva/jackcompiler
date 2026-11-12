
"""Compilador Jack para código VM."""

from symbol_table import SymbolTable
from vm_writer import VMWriter


class CompilationEngine:
    """Converte tokens Jack em instruções da máquina virtual."""

    OPERATORS = {
        "+": "add",
        "-": "sub",
        "&": "and",
        "|": "or",
        "<": "lt",
        ">": "gt",
        "=": "eq",
    }

    SEGMENTS = {
        "static": "static",
        "field": "this",
        "arg": "argument",
        "var": "local",
    }

    def __init__(self, tokens, output_path):
        self.tokens = list(tokens)
        self.position = 0
        self.symbol_table = SymbolTable()
        self.vm_writer = VMWriter(output_path)
        self.class_name = ""
        self.label_counter = 0

    def peek(self, offset=0):
        index = self.position + offset
        if index < len(self.tokens):
            return self.tokens[index]
        return None

    def advance(self):
        token = self.peek()
        if token is None:
            raise SyntaxError("Fim inesperado do arquivo.")
        self.position += 1
        return token

    def match(self, token_type, value=None):
        token = self.peek()
        return (
            token is not None
            and token[0] == token_type
            and (value is None or token[1] == value)
        )

    def consume(self, token_type, value=None):
        token = self.peek()
        if not self.match(token_type, value):
            raise SyntaxError(
                f"Token inesperado: {token}. "
                f"Esperado: {token_type} {value or ''}"
            )
        return self.advance()[1]

    def new_label(self, prefix):
        label = f"{prefix}{self.label_counter}"
        self.label_counter += 1
        return label

    def compile_type(self, allow_void=False):
        valid = {"int", "char", "boolean"}
        if allow_void:
            valid.add("void")

        if self.match("keyword") and self.peek()[1] in valid:
            return self.advance()[1]

        if self.match("identifier"):
            return self.advance()[1]

        raise SyntaxError("Tipo inválido.")

    def compile_class(self):
        self.consume("keyword", "class")
        self.class_name = self.consume("identifier")
        self.consume("symbol", "{")

        while self.match("keyword") and self.peek()[1] in {
            "static", "field"
        }:
            self.compile_class_var_dec()

        while self.match("keyword") and self.peek()[1] in {
            "constructor", "function", "method"
        }:
            self.compile_subroutine()

        self.consume("symbol", "}")

        if self.peek() is not None:
            raise SyntaxError("Tokens após o fim da classe.")

        self.vm_writer.close()

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
        while self.match("keyword") and self.peek()[1] in {
            "let", "if", "while", "do", "return"
        }:
            keyword = self.peek()[1]

            if keyword == "let":
                self.compile_let()
            elif keyword == "if":
                self.compile_if()
            elif keyword == "while":
                self.compile_while()
            elif keyword == "do":
                self.compile_do()
            elif keyword == "return":
                self.compile_return()

    def variable_info(self, name):
        kind = self.symbol_table.kind_of(name)
        index = self.symbol_table.index_of(name)

        if kind is None:
            raise SyntaxError(f"Variável não declarada: {name}")

        return self.SEGMENTS[kind], index

    def push_variable(self, name):
        segment, index = self.variable_info(name)
        self.vm_writer.write_push(segment, index)

    def pop_variable(self, name):
        segment, index = self.variable_info(name)
        self.vm_writer.write_pop(segment, index)

    def compile_let(self):
        self.consume("keyword", "let")
        name = self.consume("identifier")

        is_array = self.match("symbol", "[")

        if is_array:
            self.push_variable(name)
            self.consume("symbol", "[")
            self.compile_expression()
            self.consume("symbol", "]")
            self.vm_writer.write_arithmetic("add")

        self.consume("symbol", "=")
        self.compile_expression()
        self.consume("symbol", ";")

        if is_array:
            self.vm_writer.write_pop("temp", 0)
            self.vm_writer.write_pop("pointer", 1)
            self.vm_writer.write_push("temp", 0)
            self.vm_writer.write_pop("that", 0)
        else:
            self.pop_variable(name)

    def compile_if(self):
        self.consume("keyword", "if")
        self.consume("symbol", "(")
        self.compile_expression()
        self.consume("symbol", ")")

        true_label = self.new_label("IF_TRUE")
        false_label = self.new_label("IF_FALSE")
        end_label = self.new_label("IF_END")

        self.vm_writer.write_if(true_label)
        self.vm_writer.write_goto(false_label)
        self.vm_writer.write_label(true_label)

        self.consume("symbol", "{")
        self.compile_statements()
        self.consume("symbol", "}")

        if self.match("keyword", "else"):
            self.vm_writer.write_goto(end_label)
            self.vm_writer.write_label(false_label)

            self.consume("keyword", "else")
            self.consume("symbol", "{")
            self.compile_statements()
            self.consume("symbol", "}")

            self.vm_writer.write_label(end_label)
        else:
            self.vm_writer.write_label(false_label)

    def compile_while(self):
        start_label = self.new_label("WHILE_EXP")
        end_label = self.new_label("WHILE_END")

        self.vm_writer.write_label(start_label)

        self.consume("keyword", "while")
        self.consume("symbol", "(")
        self.compile_expression()
        self.consume("symbol", ")")

        self.vm_writer.write_arithmetic("not")
        self.vm_writer.write_if(end_label)

        self.consume("symbol", "{")
        self.compile_statements()
        self.consume("symbol", "}")

        self.vm_writer.write_goto(start_label)
        self.vm_writer.write_label(end_label)

    def compile_do(self):
        self.consume("keyword", "do")
        name = self.consume("identifier")
        self.compile_subroutine_call(name)
        self.consume("symbol", ";")
        self.vm_writer.write_pop("temp", 0)

    def compile_return(self):
        self.consume("keyword", "return")

        if self.match("symbol", ";"):
            self.vm_writer.write_push("constant", 0)
        else:
            self.compile_expression()

        self.consume("symbol", ";")
        self.vm_writer.write_return()

    def compile_expression(self):
        self.compile_term()

        while self.match("symbol") and self.peek()[1] in {
            "+", "-", "*", "/", "&", "|", "<", ">", "="
        }:
            operator = self.advance()[1]
            self.compile_term()

            if operator == "*":
                self.vm_writer.write_call("Math.multiply", 2)
            elif operator == "/":
                self.vm_writer.write_call("Math.divide", 2)
            else:
                self.vm_writer.write_arithmetic(
                    self.OPERATORS[operator]
                )

    def compile_term(self):
        token = self.peek()

        if token is None:
            raise SyntaxError("Termo esperado.")

        token_type, value = token

        if token_type == "integerConstant":
            self.advance()
            self.vm_writer.write_push("constant", int(value))

        elif token_type == "stringConstant":
            self.advance()
            self.vm_writer.write_push("constant", len(value))
            self.vm_writer.write_call("String.new", 1)

            for character in value:
                self.vm_writer.write_push("constant", ord(character))
                self.vm_writer.write_call("String.appendChar", 2)

        elif token_type == "keyword" and value in {
            "true", "false", "null", "this"
        }:
            self.advance()

            if value == "true":
                self.vm_writer.write_push("constant", 0)
                self.vm_writer.write_arithmetic("not")
            elif value in {"false", "null"}:
                self.vm_writer.write_push("constant", 0)
            else:
                self.vm_writer.write_push("pointer", 0)

        elif token_type == "symbol" and value in {"-", "~"}:
            self.advance()
            self.compile_term()
            self.vm_writer.write_arithmetic(
                "neg" if value == "-" else "not"
            )

        elif token_type == "symbol" and value == "(":
            self.consume("symbol", "(")
            self.compile_expression()
            self.consume("symbol", ")")

        elif token_type == "identifier":
            name = self.consume("identifier")

            if self.match("symbol", "["):
                self.compile_array_access(name)

            elif self.match("symbol", "(") or self.match("symbol", "."):
                self.compile_subroutine_call(name)

            else:
                self.push_variable(name)

        else:
            raise SyntaxError(f"Termo inválido: {token}")

    def compile_array_access(self, name):
        self.push_variable(name)

        self.consume("symbol", "[")
        self.compile_expression()
        self.consume("symbol", "]")

        self.vm_writer.write_arithmetic("add")
        self.vm_writer.write_pop("pointer", 1)
        self.vm_writer.write_push("that", 0)

    def compile_subroutine_call(self, name):
        n_args = 0

        if self.match("symbol", "."):
            self.consume("symbol", ".")
            subroutine_name = self.consume("identifier")

            kind = self.symbol_table.kind_of(name)

            if kind is not None:
                type_ = self.symbol_table.type_of(name)
                self.push_variable(name)
                n_args = 1
                full_name = f"{type_}.{subroutine_name}"
            else:
                full_name = f"{name}.{subroutine_name}"

        else:
            self.vm_writer.write_push("pointer", 0)
            n_args = 1
            full_name = f"{self.class_name}.{name}"

        self.consume("symbol", "(")
        n_args += self.compile_expression_list()
        self.consume("symbol", ")")

        self.vm_writer.write_call(full_name, n_args)

    def compile_expression_list(self):
        count = 0

        if not self.match("symbol", ")"):
            self.compile_expression()
            count += 1

            while self.match("symbol", ","):
                self.consume("symbol", ",")
                self.compile_expression()
                count += 1

        return count
