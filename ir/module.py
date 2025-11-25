# ir/module.py
from .function import Function

class Module:
    def __init__(self):
        self.functions = []     # funciones (normales y extern)
        self.globals = []       # variables globales
        self.strings = []       # strings como constantes globales
        self.string_id = 0      # contador para @.str0, @.str1, ...

    # ----------------------------------------------------------
    # Funciones
    # ----------------------------------------------------------
    def add_function(self, func: Function):
        self.functions.append(func)

    def add_extern(self, name, rettype, param_types):
        """
        Registra funciones externas como:
            declare void @print_string(i8*)
        """
        f = Function(name, rettype, param_types,
                     param_names=None,
                     is_extern=True)
        self.functions.append(f)
        return f

    def get_function(self, name):
        for f in self.functions:
            if f.name == name:
                return f
        return None

    # ----------------------------------------------------------
    # Globales (variables)
    # ----------------------------------------------------------
    def add_global(self, g):
        self.globals.append(g)

    def get_global(self, name):
        for g in self.globals:
            if g.name == name:
                return g
        return None

    # ----------------------------------------------------------
    # STRINGS: constantes globales estilo LLVM
    # ----------------------------------------------------------
    def add_string(self, text):
        """
        Guarda una cadena como global de solo lectura estilo LLVM:
            @.str0 = private constant [N x i8] c"..."
        Devuelve (name, llvm_type)
        """
        sid = self.string_id
        self.string_id += 1

        raw = text.encode("utf-8")
        size = len(raw) + 1  # null terminator

        name = f".str{sid}"
        llvm_type = f"[{size} x i8]"

        self.strings.append((name, llvm_type, raw))
        return name, llvm_type

    # ----------------------------------------------------------
    # Impresión del módulo entero
    # ----------------------------------------------------------
    def __str__(self):
        out = ""

        # ---- Strings primero ----
        for (name, ty, bytestr) in self.strings:

            # Convertir bytes → octal \ooo
            octal = "".join([f"\\{b:03o}" for b in bytestr]) + "\\000"

            out += f"@{name} = private constant {ty} c\"{octal}\"\n"

        # ---- Variables globales ----
        for g in self.globals:
            out += str(g) + "\n"

        # ---- Funciones ----
        for f in self.functions:
            if f.is_extern:
                params = ", ".join(f.param_types)
                out += f"declare {f.rettype} @{f.name}({params})\n"
            else:
                out += str(f)

        return out
