#implementacao do analisador
import re


KEYWORDS = {
    "class", "constructor", "function", "method", "field", "static",
    "var", "int", "char", "boolean", "void", "true", "false", "null",
    "this", "let", "do", "if", "else", "while", "return"
}

SYMBOLS = set("{}()[].,;+-*/&|<>=~") # reconhece simbolos


class Lexer:
    def __init__(self, source):
        self.source = source

    def remove_comments(self):
        pattern = r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/'
        return re.sub(
            pattern,
            lambda match: match.group(0)
            if match.group(0).startswith('"')
            else "",
            self.source,
            flags=re.DOTALL
        )

    def tokenize(self): # percorre o codigo, separa elementos e gera erro em caracteres invalidos
        source = self.remove_comments() # remove comentários (// e /*...*/) sem afetar texto dentro de strings
        tokens = []
        i = 0

        while i < len(source):
            char = source[i]

            if char.isspace():
                i += 1
                continue

            if char in SYMBOLS: # reconhece simbolos
                tokens.append(("symbol", char))
                i += 1
                continue

            if char == '"':
                end = source.find('"', i + 1)
                if end == -1:
                    raise ValueError("String sem aspas de fechamento.")

                value = source[i + 1:end]
                if "\n" in value or "\r" in value:
                    raise ValueError("String não pode atravessar linhas.")

                tokens.append(("stringConstant", value))
                i = end + 1
                continue

            if char.isdigit():
                start = i

                while i < len(source) and source[i].isdigit():
                    i += 1

                value = source[start:i]
                number = int(value)

                if number > 32767:
                    raise ValueError(
                        f"Constante inteira fora do intervalo: {value}"
                    )

                tokens.append(("integerConstant", value))
                continue

            if char.isalpha() or char == "_":
                start = i

                while (
                    i < len(source)
                    and (source[i].isalnum() or source[i] == "_")
                ):
                    i += 1

                value = source[start:i]

                if value in KEYWORDS: # guarda as palavras reservadas da linguagem Jack
                    tokens.append(("keyword", value))
                else:
                    tokens.append(("identifier", value))

                continue

            raise ValueError(
                f"Caractere inválido: {char!r} na posição {i}"
            )

        return tokens
