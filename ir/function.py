from ir.block import Block
from ir.value import Value

class Function:
    def __init__(self, name, rettype, param_types, param_names=None, is_extern=False):
        self.name = name
        self.rettype = rettype
        self.param_types = param_types
        self.blocks = []
        self.is_extern = is_extern

        self.params = []

        if not is_extern:
            # Usar nombres reales del AST
            for pname, ptype in zip(param_names, param_types):
                self.params.append(Value("%" + pname, ptype))
        else:
            # Extern: solo tipos
            for ptype in param_types:
                self.params.append(Value("", ptype))
    def new_temp(self, typ):
        """
        Crea un nombre temporal único como %t1, %t2, %t3...
        """
        if not hasattr(self, "_temp_id"):
            self._temp_id = 0
        name = f"%t{self._temp_id}"
        self._temp_id += 1
        from ir.value import Value
        return Value(name, typ)

    def new_block(self, name):
        b = Block(name)
        self.blocks.append(b)
        return b

    def __str__(self):
        if self.is_extern:
            plist = ", ".join(self.param_types)
            return f"declare {self.rettype} @{self.name}({plist})\n"

        plist = ", ".join(f"{p.type} {p}" for p in self.params)

        out = f"define {self.rettype} @{self.name}({plist}) {{\n"

        for b in self.blocks:
            # NO imprimir bloques vacíos
            if len(b.instructions) > 0:
                out += str(b)

        out += "}\n"
        return out
