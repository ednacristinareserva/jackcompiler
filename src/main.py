
import sys # integra com o terminal
from pathlib import Path

from lexer import Lexer # importa o analisador em lexer.py

def main():
    if len(sys.argv) != 2:
        print("Uso: python src/main.py <arquivo.jack>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.is_file():
        print(f"Erro: arquivo não encontrado: {file_path}")
        sys.exit(1)

    try:
        source = file_path.read_text(encoding="utf-8") # localiza e verificar o arquivo
        lexer = Lexer(source) 
        tokens = lexer.tokenize() # identifica os tokens

        for token_type, value in tokens:
            print(f"{token_type}: {value}")

    except (ValueError, OSError) as error:
        print(f"Erro ao analisar o arquivo: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
