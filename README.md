# JackCompiler — Analisador Léxico e Sintático

## 1. Sobre o projeto

Este projeto consiste na implementação de um analisador léxico e sintático para a linguagem Jack, desenvolvida no contexto do projeto JackCompiler do curso Nand2Tetris.

O analisador léxico é responsável por ler um arquivo de código-fonte `.jack`, identificar os elementos da linguagem e gerar um arquivo XML contendo os tokens reconhecidos.

O analisador sintático utiliza os tokens identificados pelo analisador léxico para verificar a estrutura gramatical do código Jack e gerar um arquivo XML representando a árvore sintática.

O projeto faz parte da disciplina EECP0026 - Compiladores, ministrada pelo Docente Dr. Sergio Souza Costa e corresponde às etapas de análise léxica e sintática do compilador Jack.

## 2. Objetivos

- Identificar palavras-chave da linguagem Jack.
- Reconhecer símbolos, constantes inteiras, constantes de texto e identificadores.
- Ignorar espaços em branco, tabulações, quebras de linha e comentários.
- Gerar um arquivo XML com os tokens encontrados.
- Analisar a estrutura sintática de programas escritos em Jack.
- Gerar um arquivo XML representando a árvore sintática.
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
│   ├── lexer.py
│   └── parser.py
├── tests/
│   ├── test_lexer.py
│   └── test_parser.py
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

Na raiz do projeto, execute o comando abaixo para analisar lexicalmente um arquivo Jack:

```bash
python src/main.py examples/Teste.jack
```

O programa lê o arquivo indicado, identifica os tokens e gera um arquivo XML correspondente. Para o exemplo acima, o arquivo de saída será `examples/TesteT.xml`.

Para analisar sintaticamente um arquivo Jack, o programa também pode receber o caminho de saída como segundo argumento:

```bash
python src/main.py examples/Teste.jack examples/TesteP.xml
```

Nesse caso, o arquivo XML de saída representa a árvore sintática do programa.

Para analisar outro arquivo, substitua o caminho pelo arquivo `.jack` desejado.

## 7. Como executar os testes

Na raiz do projeto, execute:

```bash
python -m unittest discover -s tests -v
```

O comando executa os testes automatizados para verificar o reconhecimento dos tokens, o tratamento de situações inválidas e a estrutura sintática dos programas Jack.

## 8. Validação

O projeto utiliza arquivos da linguagem Jack, incluindo `Main.jack`, `Square.jack` e `SquareGame.jack`.

Para validar o analisador léxico, os arquivos XML gerados podem ser comparados com os respectivos arquivos XML de referência, como `MainT.xml`, `SquareT.xml` e `SquareGameT.xml`.

Para validar o analisador sintático, os arquivos XML gerados podem ser comparados com `MainP.xml`, `SquareP.xml` e `SquareGameP.xml`, disponibilizados como referências oficiais.

Quando os arquivos são idênticos, a comparação não apresenta diferenças.

## 9. Integrantes

- **Discente:** Edna Cristina Durans Santos — Matrícula: 20260038268
- **Discente:** Cleila Monteiro Dutra Galiz — Matrícula: 2023027500

## 10. Verificação dos arquivos de referência

Os arquivos gerados pelo analisador léxico podem ser comparados com os XMLs de referência usando o PowerShell:

```powershell
Compare-Object (Get-Content examples/referencias/MainT.xml) (Get-Content examples/oficiais/MainT.xml)
Compare-Object (Get-Content examples/referencias/SquareT.xml) (Get-Content examples/oficiais/SquareT.xml)
Compare-Object (Get-Content examples/referencias/SquareGameT.xml) (Get-Content examples/oficiais/SquareGameT.xml)
```

Quando os arquivos são idênticos, o comando `Compare-Object` não apresenta diferenças.

Os testes automatizados podem ser executados com:

```powershell
python -m unittest discover -s tests -v
```

## 11. Repositório

Código-fonte e histórico de desenvolvimento disponíveis em:

https://github.com/ednacristinareserva/jackcompiler
