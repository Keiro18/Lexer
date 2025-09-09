from dataclasses import dataclass, field
from multimethod import multimeta, multimethod
from typing      import List, Union

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


# =====================================================================
# Definiciones de alto nivel
# =====================================================================
@dataclass
class Program(Statement):
    body: List[Statement] = field(default_factory=list)

@dataclass
class Declaration(Statement):
    pass

@dataclass
class VarDecl(Declaration):
    name : str
    type : Expression
    value: Expression = None


'''
Statement
  |
  +-- Declaration (abstract)
  | |
  | +-- VarDecl: Guardar la información de una declaración de variable
  | |
  | +-- ArrayDecl: Declaración de Arreglos (multi-dimencioanles)
  | |
  | +-- FuncDecl: Para guardar información sobre las funciones declaradas

    -- VarParm
    -- ArrayParm

  -- IfStmt
  -- ReturnStmt
  |
  +-- PrintStmt
  |
  +-- ForStmt
  |
  +-- WhileStmt
  |
  +-- DoWhileStmt
  |
  +-- Assignment
'''

# =====================================================================
# Nodos de Control de Flujo
# =====================================================================
@dataclass
class WhileStmt(Statement):
    condition: Expression
    body     : Statement

@dataclass
class DoWhileStmt(Statement):
    body     : Statement
    condition: Expression


# =====================================================================
# Expresiones básicas
# =====================================================================

@dataclass
class BinOper(Expression):
    oper : str
    left : Expression
    right: Expression

@dataclass
class UnaryOper(Expression):
    oper : str
    expr : Expression

@dataclass
class Literal(Expression):
    value : Union[int, float, str, bool]
    type  : str = None

@dataclass
class Integer(Literal):
    value : int

    def __post_init__(self):
        assert isinstance(self.value, int), "Value debe ser un 'integer'"
        self.type = 'integer'

@dataclass
class Float(Literal):
    value : float

    def __post_init__(self):
        assert isinstance(self.value, float), "Value debe ser un 'float'"
        self.type = 'float'

@dataclass
class Boolean(Literal):
    value : bool

    def __post_init__(self):
        assert isinstance(self.value, bool), "Value debe ser un 'boolean'"
        self.type = 'boolean'


# =====================================================================
# Literales adicionales
# =====================================================================
@dataclass
class Char(Literal):
    value : str
    def __post_init__(self):
        assert isinstance(self.value, str) and len(self.value) == 1, "Value debe ser un 'char'"
        self.type = 'char'

@dataclass
class String(Literal):
    value : str
    def __post_init__(self):
        assert isinstance(self.value, str), "Value debe ser un 'string'"
        self.type = 'string'


# =====================================================================
# Incremento / Decremento
# =====================================================================
@dataclass
class PreInc(Expression):
    expr: Expression

@dataclass
class PreDec(Expression):
    expr: Expression

@dataclass
class PostInc(Expression):
    expr: Expression

@dataclass
class PostDec(Expression):
    expr: Expression


# =====================================================================
# Funciones y llamadas
# =====================================================================
@dataclass
class FuncCall(Expression):
    name: str
    args: List[Expression] = field(default_factory=list)


# =====================================================================
# Ubicaciones (Locations)
# =====================================================================
@dataclass
class Location(Expression):
    name: str

@dataclass
class VarLoc(Location):
    pass

@dataclass
class ArrayLoc(Location):
    index: Expression