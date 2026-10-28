"""Ponto de entrada do JackCompiler: scanner + parser.

Para executar:
    python src/main.py arquivo.jack
    python src/main.py arquivo.jack saida.xml

Se o arquivo de saída não for informado, será criado um XML com o nome do arquivo de entrada seguido de P, na mesma pasta.
"""
import sys
from pathlib import Path

try:
    from lexer import Lexer
    from parser import Parser, ParserError
except ImportError:  # permite importação como pacote: src.main
    from src.lexer import Lexer
    from src.parser import Parser, ParserError


def compile_file(input_path, output_path=None):
    """Executa o scanner e o parser; retorna (quantidade_de_tokens, caminho_xml)."""
    input_path = Path(input_path)

    if input_path.suffix.lower() != ".jack":
        raise ValueError("O arquivo de entrada deve ter a extensão .jack.")
    if not input_path.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

    source = input_path.read_text(encoding="utf-8")
    tokens = Lexer(source).tokenize()
    xml_content = Parser(tokens).parse()

    if output_path is None:
        output_path = input_path.with_name(f"{input_path.stem}P.xml")
    else:
        output_path = Path(output_path)

    output_path.write_text(xml_content, encoding="utf-8")
    return len(tokens), output_path


def main():
    if len(sys.argv) not in (2, 3):
        print("Uso: python src/main.py <arquivo.jack> [saida.xml]")
        return 2

    try:
        token_count, output_path = compile_file(
            sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else None
        )
    except (ValueError, OSError, ParserError) as error:
        print(f"Erro ao compilar: {error}", file=sys.stderr)
        return 1

    print(f"Análise sintática concluída: {token_count} tokens analisados.")
    print(f"Arquivo XML gerado: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
