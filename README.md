# UNIVERSIDADE FEDERAL DO MARANHAO - UFMA
# EECP0026 - COMPILADORES
# Docente: Dr. Sergio Souza Costa

# JackCompiler — Analisador Léxico

## 1. Sobre o projeto

Este projeto consiste na implementação de um analisador léxico para a linguagem Jack, desenvolvida no contexto do projeto JackCompiler do curso Nand2Tetris.

O analisador léxico é responsável por ler um arquivo de código-fonte `.jack`, identificar os elementos da linguagem e gerar um arquivo XML contendo os tokens reconhecidos.

O projeto faz parte da disciplina de Compiladores e corresponde à primeira etapa de desenvolvimento do compilador Jack.

## 2. Objetivos

- Identificar palavras-chave da linguagem Jack.
- Reconhecer símbolos, constantes inteiras, constantes de texto e identificadores.
- Ignorar espaços em branco, tabulações, quebras de linha e comentários.
- Gerar um arquivo XML com os tokens encontrados.
- Validar o funcionamento por meio de testes automatizados e arquivos de referência oficiais.

## 3. Tecnologias utilizadas

- **Linguagem:** Python 3
- **Testes:** unittest
- **Formato de saída:** XML
- **Controle de versão:** Git e GitHub

## 4. Estrutura do projeto

```text
jackcompiler/
├── src/
│   ├── main.py
│   └── lexer.py
├── tests/
│   └── test_lexer.py
├── examples/
│   ├── Teste.jack
│   ├── TesteT.xml
│   ├── oficiais/
│   │   ├── Main.jack
│   │   ├── MainT.xml
│   │   ├── Square.jack
│   │   ├── SquareT.xml
│   │   ├── SquareGame.jack
│   │   └── SquareGameT.xml
│   └── referencias/
├── tools/
├── README.md
└── .gitignore
```

## 5. Tipos de tokens reconhecidos

O analisador identifica cinco categorias de tokens:

- **keyword:** palavras reservadas da linguagem, como `class`, `function`, `int` e `return`.
- **symbol:** símbolos da linguagem, como `{`, `}`, `(`, `)`, `;` e `=`.
- **integerConstant:** constantes inteiras entre 0 e 32767.
- **stringConstant:** constantes de texto delimitadas por aspas duplas.
- **identifier:** nomes utilizados para identificar classes, variáveis, métodos e outros elementos.

Comentários de linha (`//`) e de bloco (`/* ... */`), assim como espaços em branco, são ignorados durante a análise.

## 6. Como executar

É necessário ter o Python 3 instalado.

Na raiz do projeto, execute o comando abaixo para analisar um arquivo Jack:

```bash
python src/main.py examples/Teste.jack
```

O programa lê o arquivo indicado, identifica os tokens e gera um arquivo XML correspondente. Para o exemplo acima, o arquivo de saída será `examples/TesteT.xml`.

Para analisar outro arquivo, substitua o caminho pelo arquivo `.jack` desejado.

## 7. Como executar os testes

Na raiz do projeto, execute:

```bash
python -m unittest discover -s tests -v
```

O comando executa os testes automatizados para verificar o reconhecimento dos tokens e o tratamento de situações como comentários, strings sem fechamento e caracteres inválidos.

## 8. Validação

O projeto foi testado com arquivos da linguagem Jack, incluindo `Main.jack`, `Square.jack` e `SquareGame.jack`.

Os arquivos XML gerados foram comparados com os respectivos arquivos XML de referência. A comparação sem diferenças indica que as saídas são idênticas às referências utilizadas.

## 9. Integrantes

- **Discente:** [Edna Cristina Durans Santos] — Matrícula: [20260038268]
- **Discente:** [Cleila Monteiro Dutra Galiz] — Matrícula: [2023027500]


## 10. Repositório

Código-fonte e histórico de desenvolvimento disponíveis em:

https://github.com/ednacristinareserva/jackcompiler
