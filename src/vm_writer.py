
"""Escritor de comandos da máquina virtual Jack."""

class VMWriter:
    """Gera instruções VM e as armazena em um arquivo de saída."""

    def __init__(self, output_path):
        self.output_path = output_path
        self.commands = []

    def write_push(self, segment, index):
        """Escreve: push segmento índice."""
        self.commands.append(f"push {segment} {index}")

    def write_pop(self, segment, index):
        """Escreve: pop segmento índice."""
        self.commands.append(f"pop {segment} {index}")

    def write_arithmetic(self, command):
        """Escreve uma operação aritmética ou lógica."""
        valid_commands = {
            "add", "sub", "neg",
            "eq", "gt", "lt",
            "and", "or", "not"
        }

        if command not in valid_commands:
            raise ValueError(f"Comando aritmético inválido: {command}")

        self.commands.append(command)

    def write_label(self, label):
        """Escreve: label nome."""
        self.commands.append(f"label {label}")

    def write_goto(self, label):
        """Escreve: goto nome."""
        self.commands.append(f"goto {label}")

    def write_if(self, label):
        """Escreve: if-goto nome."""
        self.commands.append(f"if-goto {label}")

    def write_call(self, name, n_args):
        """Escreve: call nome quantidade_de_argumentos."""
        self.commands.append(f"call {name} {n_args}")

    def write_function(self, name, n_locals):
        """Escreve: function nome quantidade_de_locais."""
        self.commands.append(f"function {name} {n_locals}")

    def write_return(self):
        """Escreve: return."""
        self.commands.append("return")

    def close(self):
        """Grava todas as instruções no arquivo .vm."""
        with open(self.output_path, "w", encoding="utf-8") as file:
            for command in self.commands:
                file.write(command + "\n")
