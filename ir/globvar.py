# ir/global.py

class Global:
    def __init__(self, name, typ, init_value=None):
        self.name = name
        self.type = typ     # ej: "i32"
        self.init = init_value  # Constant o None

    def __str__(self):
        if self.init is None:
            return f"@{self.name} = global {self.type} 0"
        return f"@{self.name} = global {self.type} {self.init}"
