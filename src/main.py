
import sys
from html import escape
from pathlib import Path

from lexer import Lexer
from parser import Parser, ParserError


def tokens_to_xml(tokens):
    lines = ["<tokens>"]

    for token_type, value in tokens:
        safe_value = escape(value, quote=False)
        lines.append(f"<{token_type}> {safe_value} </{token_type}>")

    lines.append("</tokens>")
    return "\n".join(lines) + "\n"


def compile_file(mode, input_path):
    input_path = Path(input_path)

    if input_path.suffix.lower() != ".jack":
        raise ValueError("O arquivo deve ter a extensão .jack.")

    if not input_path.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

    source = input_path.read_text(encoding="utf-8")
    tokens = Lexer(source).tokenize()

    if mode == "lexer":
        output_path = input_path.with_name(f"{input_path.stem}T.xml")
        content = tokens_to_xml(tokens)

    elif mode == "parser":
        output_path = input_path.with_name(f"{input_path.stem}P.xml")
        content = Parser(tokens).parse()

    else:
        raise ValueError("Modo inválido. Use 'lexer' ou 'parser'.")

    output_path.write_text(content, encoding="utf-8")

    return len(tokens), output_path


def main():
    if len(sys.argv) != 3:
        print("Uso:")
        print("  python src/main.py lexer arquivo.jack")
        print("  python src/main.py parser arquivo.jack")
        return 1

    mode = sys.argv[1].lower()

    if mode not in ("lexer", "parser"):
        print("Erro: o modo deve ser 'lexer' ou 'parser'.")
        return 1

    try:
        token_count, output_path = compile_file(mode, sys.argv[2])
        print(f"Análise concluída: {token_count} tokens encontrados.")
        print(f"Arquivo XML gerado: {output_path}")
        return 0

    except (ValueError, OSError, ParserError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
