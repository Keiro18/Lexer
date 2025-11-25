from ir.instr import Instruction
from ir.value import Temp

class Alloca(Instruction):
    def __init__(self, typ, result):
        super().__init__()
        self.typ = typ
        self.result = result

    def __str__(self):
        return f"{self.result} = alloca {self.typ}"

class Store(Instruction):
    def __init__(self, value, ptr):
        super().__init__()
        self.value = value
        self.ptr = ptr

    def __str__(self):
        return f"store {self.value.type} {self.value}, {self.value.type}* {self.ptr}"

class Load(Instruction):
    def __init__(self, ptr, result):
        super().__init__()
        self.ptr = ptr
        self.result = result

    def __str__(self):
        return f"{self.result} = load {self.result.type}, {self.result.type}* {self.ptr}"
