# bminor_ast.py
# Definición de nodos del AST para B-Minor

from dataclasses import dataclass, field
from multimethod import multimeta, multimethod
from typing import List, Union

# =====================================================================
# Clases Abstractas
# =====================================================================
class Visitor(metaclass=multimeta):
    pass

@dataclass
class Node:
    def accept(self, v: Visitor, *args, **kwargs):
        return v.visit(self, *args, **kwargs)

@dataclass
class Statement(Node):
    pass

@dataclass
class Expression(Node):
    pass

@dataclass
class Declaration(Statement):
    pass

# =====================================================================
# Programa
# =====================================================================
@dataclass
class Program(Statement):
    body: List[Statement] = field(default_factory=list)

# =====================================================================
# Declaraciones
# =====================================================================
@dataclass
class VarDecl(Declaration):
    name: str
    type: Expression
    value: Expression = None

@dataclass
class VarDeclInit(Declaration):
    name: str
    typ: Expression
    init: Expression = None

class FuncDecl(Declaration):
    def __init__(self, name, type_func, body=None):
        self.name = name
        self.type_func = type_func
        self.body = body if body else []

# =====================================================================
# Tipos
# =====================================================================
class SimpleType(Node):
    def __init__(self, name):
        self.name = name

class ArrayType(Node):
    def __init__(self, size, elem_type):
        self.size = size
        self.elem_type = elem_type

class FuncType(Node):
    def __init__(self, ret_type, params):
        self.ret_type = ret_type
        self.params = params if params else []

class Param(Node):
    def __init__(self, name, typ):
        self.name = name
        self.typ = typ

# =====================================================================
# Sentencias de Control
# =====================================================================
class IfStmt(Statement):
    def __init__(self, cond, then_branch, else_branch=None):
        self.cond = cond
        self.then_branch = then_branch
        self.else_branch = else_branch

class WhileStmt(Statement):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

class DoWhileStmt(Statement):
    def __init__(self, body, cond):
        self.body = body
        self.cond = cond

class ForStmt(Statement):
    def __init__(self, init, cond, step, body):
        self.init = init
        self.cond = cond
        self.step = step
        self.body = body

class ReturnStmt(Statement):
    def __init__(self, expr):
        self.expr = expr

@dataclass
class PrintStmt(Statement):
    expr: Expression

class Block(Statement):
    def __init__(self, body):
        self.body = body if body else []

# =====================================================================
# Expresiones Binarias y Unarias
# =====================================================================
@dataclass
class BinOper(Expression):
    oper: str
    left: Expression
    right: Expression = None

@dataclass
class UnaryOper(Expression):
    oper: str
    expr: Expression

# =====================================================================
# Operaciones de Incremento/Decremento
# =====================================================================
class PreInc(Expression):
    def __init__(self, expr):
        self.expr = expr

class PreDec(Expression):
    def __init__(self, expr):
        self.expr = expr

# =====================================================================
# Asignación y Llamadas
# =====================================================================
class Assign(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class Call(Expression):
    def __init__(self, func, args):
        self.func = func
        self.args = args if args else []

class ArrayAccess(Expression):
    def __init__(self, array, index):
        self.array = array
        self.index = index

# =====================================================================
# Identificadores
# =====================================================================
class Identifier(Expression):
    def __init__(self, name):
        self.name = name

# =====================================================================
# Literales
# =====================================================================
@dataclass
class Literal(Expression):
    value: Union[int, float, str, bool]
    type: str = None

@dataclass
class Integer(Literal):
    value: int

    def __post_init__(self):
        assert isinstance(self.value, int), "Value debe ser un 'integer'"
        self.type = 'integer'

@dataclass
class Float(Literal):
    value: float

    def __post_init__(self):
        assert isinstance(self.value, float), "Value debe ser un 'float'"
        self.type = 'float'

@dataclass
class Boolean(Literal):
    value: bool

    def __post_init__(self):
        assert isinstance(self.value, bool), "Value debe ser un 'boolean'"
        self.type = 'boolean'

class Char(Literal):
    def __init__(self, value):
        self.value = value
        self.type = 'char'

class String(Literal):
    def __init__(self, value):
        self.value = value
        self.type = 'string'