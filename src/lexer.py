# palavras reservadas 
KEYWORDS = {
    "class", "constructor", "function", "method", "field", "static",
    "var", "int", "char", "boolean", "void", "true", "false", "null",
    "this", "let", "do", "if", "else", "while", "return"
}
# reconhece simbolos
SYMBOLS = set("{}()[].,;+-*/&|<>=~") # reconhece simbolos

class Lexer:
    def __init__(self, source):
        self.source = source
    # percorre o codigo, separa elementos e gera erro em caracteres invalidos
    def tokenize(self): 
        # remove comentários (// e /*...*/) sem afetar texto dentro de strings
        source = self.source 
        tokens = []
        i = 0

        while i < len(source):
            char = source[i]

            # ignora espacos, tabulacoes e quebras de linha
            if char.isspace():
                i += 1
                continue

            # ignora comentario de linha: //
            if source.startswith("//", i):
                while i < len(source) and source[i] not in "\r\n":
                    i += 1
                continue

            # ignora comentario de bloco: /* ... */
            if source.startswith("/*", i):
                end = source.find("*/", i + 2)

                if end == -1:
                    raise ValueError(
                        "Comentario de bloco sem fechamento."
                    )

                i = end + 2
                continue

            # reconhece as strings
            if char == '"':
                start = i + 1
                i += 1

                while i < len(source) and source[i] != '"':
                    if source[i] in "\r\n":
                        raise ValueError(
                            "String nao pode atravessar linhas."
                        )
                    i += 1

                if i >= len(source):
                    raise ValueError(
                        "String sem aspas de fechamento."
                    )

                value = source[start:i]
                tokens.append(("stringConstant", value))
                i += 1
                continue

            # reconhece simbolos
            if char in SYMBOLS:
                tokens.append(("symbol", char))
                i += 1
                continue

            # reconhece constantes inteiras
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

            # reconhece palavras reservadas e identificadores
            if char.isalpha() or char == "_":
                start = i

                while (
                    i < len(source)
                    and (source[i].isalnum() or source[i] == "_")
                ):
                    i += 1

                value = source[start:i]

                # guarda as palavras reservadas da linguagem jack
                if value in KEYWORDS:
                    tokens.append(("keyword", value))
                else:
                    tokens.append(("identifier", value))

                continue

            # reejeita caracteres que nao pertencem a linguagem
            raise ValueError(
                f"Caractere invalido: {char!r} na posicao {i}"
            )

        return tokens
