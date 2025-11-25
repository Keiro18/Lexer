# ir/value.py

class Value:
    """Base class for all values used in IR."""
    def __init__(self, name, typ):
        self.name = name       # string (e.g. "%t1")
        self.type = typ        # "i32", "i1", etc.

    def __str__(self):
        return f"{self.name}"


class Constant(Value):
    """IR constant values."""
    def __init__(self, value, typ):
        super().__init__(str(value), typ)
        self.value = value


class Temp(Value):
    """SSA temporary value (%t1, %t2...)."""
    def __init__(self, id, typ):
        super().__init__(f"%t{id}", typ)
        self.id = id

class GlobalRef(Value):
    """
    Representa un puntero a una variable global.
    name: nombre global, ej @x
    typ: tipo del valor que almacena
    """
    def __init__(self, name, typ):
        super().__init__(f"@{name}", f"{typ}*")
        self.name = name
        self.type = f"{typ}*"

    def __str__(self):
        return f"@{self.name}"


