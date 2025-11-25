# ir/builder.py

from .instr import BinOp, Load, Store, Branch, Jump, Return
from .value import Constant
from ir.memory import Alloca, Store, Load
from ir.instr import Call

class Builder:
    def __init__(self, function):
        self.func = function
        self.block = None

    def position_at_end(self, block):
        self.block = block

    def const(self, value, typ):
        return Constant(value, typ)

    def add(self, left, right):
        result = self.func.new_temp(left.type)
        instr = BinOp("add", left, right, result)
        self.block.append(instr)
        return result

    def ret(self, value):
        instr = Return(value)
        self.block.append(instr)
    
    def alloca(self, typ):
        temp = self.func.new_temp(f"{typ}*")
        instr = Alloca(typ, temp)
        self.block.append(instr)
        return temp

    def store(self, value, ptr):
        instr = Store(value, ptr)
        self.block.append(instr)

    def load(self, ptr, typ):
        temp = self.func.new_temp(typ)
        instr = Load(ptr, temp)
        self.block.append(instr)
        return temp
    
    def call(self, func, args):
        # registrar argumentos reales
        func.args = args

        if func.rettype == "void":
            instr = Call(func, args, None)
            self.block.append(instr)
            return None
        else:
            result = self.func.new_temp(func.rettype)
            instr = Call(func, args, result)
            self.block.append(instr)
            return result
