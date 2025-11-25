# ir/instr.py

class Instruction:
    """Base class for all IR instructions."""
    def __init__(self):
        self.parent = None   # BasicBlock that owns this instruction


class BinOp(Instruction):
    def __init__(self, op, left, right, result):
        super().__init__()
        self.op = op
        self.left = left
        self.right = right
        self.result = result

    def __str__(self):
        op = self.op

        # --- Caso: icmp_* ---
        if op.startswith("icmp_"):
            pred = op.split("_", 1)[1]    # "sgt", "slt", etc.
            return f"{self.result} = icmp {pred} {self.left.type} {self.left}, {self.right}"

        # --- Caso: fcmp_* ---
        if op.startswith("fcmp_"):
            pred = op.split("_", 1)[1]    # "ogt", "olt", etc.
            return f"{self.result} = fcmp {pred} {self.left.type} {self.left}, {self.right}"

        # --- Operaciones aritméticas estándar ---
        return f"{self.result} = {op} {self.left.type} {self.left}, {self.right}"



class Load(Instruction):
    def __init__(self, src, result):
        super().__init__()
        self.src = src
        self.result = result

    def __str__(self):
        return f"{self.result} = load {self.src.type}, {self.src.type}* {self.src}"


class Store(Instruction):
    def __init__(self, value, dst):
        super().__init__()
        self.value = value
        self.dst = dst

    def __str__(self):
        return f"store {self.value.type} {self.value}, {self.dst.type}* {self.dst}"


class Branch(Instruction):
    def __init__(self, cond, iftrue, iffalse):
        super().__init__()
        self.cond = cond
        self.iftrue = iftrue
        self.iffalse = iffalse

    def __str__(self):
        return f"br i1 {self.cond}, label %{self.iftrue.name}, label %{self.iffalse.name}"


class Jump(Instruction):
    def __init__(self, target):
        super().__init__()
        self.target = target

    def __str__(self):
        return f"br label %{self.target.name}"


class Return(Instruction):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        if self.value is None:
            return "ret void"
        return f"ret {self.value.type} {self.value}"


# ⬇⬇⬇ AÑADE ESTO AL FINAL DEL ARCHIVO ⬇⬇⬇

class Call(Instruction):
    """
    Llamada a función:
      %tN = call rettype @func(argtypes args...)
    o, si la función es void:
      call void @func(argtypes args...)
    """
    def __init__(self, func, args, result=None):
        super().__init__()
        self.func = func      # objeto Function o algo con .name y .rettype
        self.args = args      # lista de Value
        self.result = result  # Value o None si void

    def __str__(self):
        arg_str = ", ".join(f"{a.type} {a}" for a in self.args)
        if self.result is None:
            return f"call {self.func.rettype} @{self.func.name}({arg_str})"
        else:
            return f"{self.result} = call {self.func.rettype} @{self.func.name}({arg_str})"


class GetElementPtr(Instruction):
    """
    GEP real de LLVM:

    Caso array local:
        %r = getelementptr [N x T], [N x T]* %arr, i32 0, i32 idx

    Caso puntero plano:
        %r = getelementptr T, T* %base, i32 idx
    """

    def __init__(self, base_ptr, index_val, result):
        super().__init__()
        self.base_ptr = base_ptr   # Value con tipo "[N x T]*" o "T*"
        self.index_val = index_val # Value (i32)
        self.result = result       # Value con tipo "T*"

    def __str__(self):
        base_ptr_ty = self.base_ptr.type  # ej: "[25 x i32]*" o "i32*"

        # --- Caso: puntero a array [N x T]* ---
        if base_ptr_ty.startswith("[") and base_ptr_ty.endswith("*"):
            elem_ty = base_ptr_ty.rstrip("*")   # "[25 x i32]"
            return (
                f"{self.result} = getelementptr {elem_ty}, "
                f"{elem_ty}* {self.base_ptr}, i32 0, i32 {self.index_val}"
            )

        # --- Caso: puntero plano T* ---
        if base_ptr_ty.endswith("*"):
            elem_ty = base_ptr_ty.rstrip("*")   # "i32", "float", etc.
            return (
                f"{self.result} = getelementptr {elem_ty}, "
                f"{base_ptr_ty} {self.base_ptr}, i32 {self.index_val}"
            )

        # Fallback (no debería pasar normalmente)
        return (
            f"{self.result} = getelementptr {base_ptr_ty}, "
            f"{base_ptr_ty}* {self.base_ptr}, i32 0, i32 {self.index_val}"
        )


