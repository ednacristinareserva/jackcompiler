
"""Tabela de símbolos para o compilador Jack."""


class SymbolTable:
    """Gerencia símbolos nos escopos de classe e subrotina."""

    def __init__(self):
        self.class_scope = {}
        self.subroutine_scope = {}
        self.indices = {
            "static": 0,
            "field": 0,
            "arg": 0,
            "var": 0,
        }

    def start_subroutine(self):
        """Inicia um novo escopo de subrotina, limpando argumentos e locais."""
        self.subroutine_scope.clear()
        self.indices["arg"] = 0
        self.indices["var"] = 0

    def define(self, name, type_, kind):
        """Define um símbolo e atribui seu índice na categoria."""
        if kind not in self.indices:
            raise ValueError(f"Categoria inválida: {kind}")

        index = self.indices[kind]
        symbol = {
            "type": type_,
            "kind": kind,
            "index": index,
        }

        if kind in ("static", "field"):
            self.class_scope[name] = symbol
        else:
            self.subroutine_scope[name] = symbol

        self.indices[kind] += 1

    def var_count(self, kind):
        """Retorna quantos símbolos foram definidos na categoria."""
        if kind not in self.indices:
            raise ValueError(f"Categoria inválida: {kind}")
        return self.indices[kind]

    def _lookup(self, name):
        """Busca primeiro no escopo de subrotina, depois no de classe."""
        if name in self.subroutine_scope:
            return self.subroutine_scope[name]
        if name in self.class_scope:
            return self.class_scope[name]
        return None

    def kind_of(self, name):
        """Retorna a categoria do símbolo, ou None se não existir."""
        symbol = self._lookup(name)
        return symbol["kind"] if symbol else None

    def type_of(self, name):
        """Retorna o tipo do símbolo, ou None se não existir."""
        symbol = self._lookup(name)
        return symbol["type"] if symbol else None

    def index_of(self, name):
        """Retorna o índice do símbolo, ou None se não existir."""
        symbol = self._lookup(name)
        return symbol["index"] if symbol else None
