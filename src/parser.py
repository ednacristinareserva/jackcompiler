"""Analisador sintático recursivo para a linguagem Jack.

Recebe os tokens produzidos por src/lexer.py, no formato
[(tipo, valor), ...], e gera a árvore sintática em XML no formato
utilizado pelo projeto nand2tetris.
"""

from html import escape


class ParserError(Exception):
    """Erro sintático com posição aproximada no fluxo de tokens."""


class Parser:
    KEYWORD_CONSTANTS = {"true", "false", "null", "this"}
    STATEMENTS = {"let", "if", "while", "do", "return"}
    OPERATORS = {"+", "-", "*", "/", "&", "|", "<", ">", "="}
    UNARY_OPERATORS = {"-", "~"}
    TYPE_KEYWORDS = {"int", "char", "boolean"}
    SUBROUTINE_KEYWORDS = {"constructor", "function", "method"}
    CLASS_VAR_KEYWORDS = {"static", "field"}

    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.position = 0
        self.output = []
        self.indent_level = 0

    def parse(self):
        """Analisa uma classe Jack e devolve o XML completo."""
        self.output = []
        self.indent_level = 0
        self._compile_class()
        if self.position != len(self.tokens):
            token_type, value = self.tokens[self.position]
            raise self._error(
                f"Token inesperado após o fim da classe: {value!r} ({token_type})"
            )
        return "\n".join(self.output) + "\n"

    # ---------- navegação e consumo de tokens ----------

    def peek(self, offset=0):
        index = self.position + offset
        return self.tokens[index] if index < len(self.tokens) else None

    def advance(self):
        token = self.peek()
        if token is None:
            raise self._error("Fim inesperado do arquivo.")
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
        if token is None:
            expected = f"{token_type}" + (f" {value!r}" if value is not None else "")
            raise self._error(f"Fim inesperado do arquivo; esperado {expected}.")
        if token[0] != token_type or (value is not None and token[1] != value):
            expected = f"{token_type}" + (f" {value!r}" if value is not None else "")
            raise self._error(
                f"Token inesperado {token[1]!r} ({token[0]}); esperado {expected}."
            )
        return self.advance()

    def _error(self, message):
        # O lexer atual não armazena linha/coluna nos tokens; informa o índice.
        return ParserError(f"Erro sintático no token {self.position + 1}: {message}")

    # ---------- escrita de XML ----------

    def _open(self, tag):
        self.output.append("  " * self.indent_level + f"<{tag}>")
        self.indent_level += 1

    def _close(self, tag):
        self.indent_level -= 1
        self.output.append("  " * self.indent_level + f"</{tag}>")

    def _write_terminal(self):
        token_type, value = self.advance()
        safe_value = escape(value, quote=True)
        self.output.append(
            "  " * self.indent_level
            + f"<{token_type}> {safe_value} </{token_type}>"
        )

    def _eat(self, token_type, value=None):
        self.consume(token_type, value)
        self.position -= 1
        self._write_terminal()

    def _eat_symbol(self, value):
        self._eat("symbol", value)

    def _eat_keyword(self, value):
        self._eat("keyword", value)

    # ---------- gramática Jack ----------

    def _compile_class(self):
        self._open("class")
        self._eat_keyword("class")
        self._eat("identifier")
        self._eat_symbol("{")
        while self.match("keyword") and self.peek()[1] in self.CLASS_VAR_KEYWORDS:
            self._compile_class_var_dec()
        while self.match("keyword") and self.peek()[1] in self.SUBROUTINE_KEYWORDS:
            self._compile_subroutine()
        self._eat_symbol("}")
        self._close("class")

    def _compile_class_var_dec(self):
        self._open("classVarDec")
        self._write_terminal()
        self._compile_type()
        self._eat("identifier")
        while self.match("symbol", ","):
            self._eat_symbol(",")
            self._eat("identifier")
        self._eat_symbol(";")
        self._close("classVarDec")

    def _compile_type(self, allow_void=False):
        token = self.peek()
        valid_keywords = self.TYPE_KEYWORDS | ({"void"} if allow_void else set())
        if token and (
            (token[0] == "keyword" and token[1] in valid_keywords)
            or token[0] == "identifier"
        ):
            self._write_terminal()
        else:
            raise self._error("Esperado um tipo (int, char, boolean ou identificador).")

    def _compile_subroutine(self):
        self._open("subroutineDec")
        self._write_terminal()  # constructor, function ou method
        if self.match("keyword", "void"):
            self._eat_keyword("void")
        else:
            self._compile_type()
        self._eat("identifier")
        self._eat_symbol("(")
        self._compile_parameter_list()
        self._eat_symbol(")")
        self._compile_subroutine_body()
        self._close("subroutineDec")

    def _compile_parameter_list(self):
        self._open("parameterList")
        if not self.match("symbol", ")"):
            self._compile_type()
            self._eat("identifier")
            while self.match("symbol", ","):
                self._eat_symbol(",")
                self._compile_type()
                self._eat("identifier")
        self._close("parameterList")

    def _compile_subroutine_body(self):
        self._open("subroutineBody")
        self._eat_symbol("{")
        while self.match("keyword", "var"):
            self._compile_var_dec()
        self._compile_statements()
        self._eat_symbol("}")
        self._close("subroutineBody")

    def _compile_var_dec(self):
        self._open("varDec")
        self._eat_keyword("var")
        self._compile_type()
        self._eat("identifier")
        while self.match("symbol", ","):
            self._eat_symbol(",")
            self._eat("identifier")
        self._eat_symbol(";")
        self._close("varDec")

    def _compile_statements(self):
        self._open("statements")
        while self.match("keyword") and self.peek()[1] in self.STATEMENTS:
            keyword = self.peek()[1]
            if keyword == "let":
                self._compile_let()
            elif keyword == "if":
                self._compile_if()
            elif keyword == "while":
                self._compile_while()
            elif keyword == "do":
                self._compile_do()
            elif keyword == "return":
                self._compile_return()
        self._close("statements")

    def _compile_let(self):
        self._open("letStatement")
        self._eat_keyword("let")
        self._eat("identifier")
        if self.match("symbol", "["):
            self._eat_symbol("[")
            self._compile_expression()
            self._eat_symbol("]")
        self._eat_symbol("=")
        self._compile_expression()
        self._eat_symbol(";")
        self._close("letStatement")

    def _compile_if(self):
        self._open("ifStatement")
        self._eat_keyword("if")
        self._eat_symbol("(")
        self._compile_expression()
        self._eat_symbol(")")
        self._eat_symbol("{")
        self._compile_statements()
        self._eat_symbol("}")
        if self.match("keyword", "else"):
            self._eat_keyword("else")
            self._eat_symbol("{")
            self._compile_statements()
            self._eat_symbol("}")
        self._close("ifStatement")

    def _compile_while(self):
        self._open("whileStatement")
        self._eat_keyword("while")
        self._eat_symbol("(")
        self._compile_expression()
        self._eat_symbol(")")
        self._eat_symbol("{")
        self._compile_statements()
        self._eat_symbol("}")
        self._close("whileStatement")

    def _compile_do(self):
        self._open("doStatement")
        self._eat_keyword("do")
        self._compile_subroutine_call()
        self._eat_symbol(";")
        self._close("doStatement")

    def _compile_return(self):
        self._open("returnStatement")
        self._eat_keyword("return")
        if not self.match("symbol", ";"):
            self._compile_expression()
        self._eat_symbol(";")
        self._close("returnStatement")

    def _compile_expression(self):
        self._open("expression")
        self._compile_term()
        while self.match("symbol") and self.peek()[1] in self.OPERATORS:
            self._write_terminal()
            self._compile_term()
        self._close("expression")

    def _compile_term(self):
        self._open("term")
        token = self.peek()
        if token is None:
            raise self._error("Esperado um termo, mas o arquivo terminou.")

        if token[0] == "integerConstant" or token[0] == "stringConstant":
            self._write_terminal()
        elif token[0] == "keyword" and token[1] in self.KEYWORD_CONSTANTS:
            self._write_terminal()
        elif token[0] == "symbol" and token[1] in self.UNARY_OPERATORS:
            self._write_terminal()
            self._compile_term()
        elif token[0] == "symbol" and token[1] == "(":
            self._eat_symbol("(")
            self._compile_expression()
            self._eat_symbol(")")
        elif token[0] == "identifier":
            if self.peek(1) and self.peek(1) == ("symbol", "["):
                self._eat("identifier")
                self._eat_symbol("[")
                self._compile_expression()
                self._eat_symbol("]")
            elif self.peek(1) and self.peek(1)[0] == "symbol" and self.peek(1)[1] in {"(", "."}:
                self._compile_subroutine_call()
            else:
                self._eat("identifier")
        else:
            raise self._error(
                f"Termo inválido: {token[1]!r} ({token[0]})."
            )
        self._close("term")

    def _compile_subroutine_call(self):
        self._eat("identifier")
        if self.match("symbol", "."):
            self._eat_symbol(".")
            self._eat("identifier")
        self._eat_symbol("(")
        self._compile_expression_list()
        self._eat_symbol(")")

    def _compile_expression_list(self):
        self._open("expressionList")
        if not self.match("symbol", ")"):
            self._compile_expression()
            while self.match("symbol", ","):
                self._eat_symbol(",")
                self._compile_expression()
        self._close("expressionList")
