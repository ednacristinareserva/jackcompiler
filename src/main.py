
"""Interface de linha de comando do compilador Jack."""

import sys
from html import escape
from pathlib import Path

from lexer import Lexer
from parser import Parser, ParserError
from compilation_engine import CompilationEngine


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
        output_path.write_text(content, encoding="utf-8")

    elif mode == "parser":
        output_path = input_path.with_name(f"{input_path.stem}P.xml")
        content = Parser(tokens).parse()
        output_path.write_text(content, encoding="utf-8")

    elif mode == "vm":
        output_path = input_path.with_suffix(".vm")
        CompilationEngine(tokens, output_path).compile_class()

    else:
        raise ValueError("Modo inválido. Use lexer, parser ou vm.")

    return len(tokens), output_path


def compile_directory(directory):
    directory = Path(directory)

    if not directory.is_dir():
        raise NotADirectoryError(f"Diretório inválido: {directory}")

    jack_files = sorted(
        path for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() == ".jack"
    )

    if not jack_files:
        raise ValueError("Nenhum arquivo .jack encontrado no diretório.")

    results = []

    for jack_file in jack_files:
        results.append(compile_file("vm", jack_file))

    return results


def main():
    args = sys.argv[1:]

    if len(args) == 1:
        mode = "vm"
        input_path = Path(args[0])

    elif len(args) == 2:
        mode = args[0].lower()
        input_path = Path(args[1])

        if mode not in {"lexer", "parser", "vm"}:
            print("Erro: modo inválido.", file=sys.stderr)
            return 1

    else:
        print("Uso:")
        print("  python src/main.py arquivo.jack")
        print("  python src/main.py diretorio/")
        print("  python src/main.py lexer arquivo.jack")
        print("  python src/main.py parser arquivo.jack")
        print("  python src/main.py vm arquivo.jack")
        return 1

    try:
        if input_path.is_dir():
            if mode != "vm":
                raise ValueError(
                    "Diretórios são aceitos apenas no modo VM."
                )

            results = compile_directory(input_path)

            for token_count, output_path in results:
                print(
                    f"Compilado: {output_path} "
                    f"({token_count} tokens)"
                )

            print(f"Total: {len(results)} arquivo(s) compilado(s).")

        else:
            token_count, output_path = compile_file(mode, input_path)

            print(f"Análise concluída: {token_count} tokens.")
            print(f"Arquivo gerado: {output_path}")

        return 0

    except (ValueError, OSError, SyntaxError, ParserError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
