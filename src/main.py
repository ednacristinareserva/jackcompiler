
import sys # integra com o terminal
from html import escape
from pathlib import Path

# importa o analisador em lexer.py
from lexer import Lexer

# transforma a lista de tokens em XML
def tokens_to_xml(tokens):
    lines = ["<tokens>"]

    for token_type, value in tokens:
        safe_value = escape(value, quote=False) # converte os caracteres especiais para representacoes validas no XML
        lines.append(f"<{token_type}> {safe_value} </{token_type}>")

    lines.append("</tokens>")
    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) != 2:
        print("Uso: python src/main.py <arquivo.jack>")
        sys.exit(1)

  
    file_path = Path(sys.argv[1])

    if file_path.suffix.lower() != ".jack":
        print("Erro: o arquivo deve ter a extensão .jack")
        sys.exit(1)

    if not file_path.is_file():
        print(f"Erro: arquivo não encontrado: {file_path}")
        sys.exit(1)

    # localiza e verificar o arquivo
    try:
        source = file_path.read_text(encoding="utf-8")
        lexer = Lexer(source)
        tokens = lexer.tokenize() # identifica os tokens

        output_path = file_path.with_name(file_path.stem + "T.xml") # funcao with_name define o nome do arquivo de saida
        xml_content = tokens_to_xml(tokens)

        # grava primeiro em um arquivo temporario para evitar XML incompleto
        temporary_path = output_path.with_name(output_path.name + ".tmp")
        try:
            temporary_path.write_text(xml_content, encoding="utf-8")
            temporary_path.replace(output_path)
        finally:
            if temporary_path.exists():
                temporary_path.unlink()

        print(f"Análise concluída: {len(tokens)} tokens encontrados.")
        print(f"Arquivo XML gerado: {output_path}")

    except (ValueError, OSError) as error:
        print(f"Erro ao analisar o arquivo: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
