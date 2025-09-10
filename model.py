from dataclasses import dataclass, field
from multimethod import multimeta
from typing import List, Union, Optional

# =====================================================================
# Clases base
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
class Decl(Declaration): 
    name : str
    type : Expression
    value: Optional[Expression] = None


# =====================================================================
# Tipos
# =====================================================================
@dataclass
class Type(Expression):
    name: str

@dataclass
class ArrayType(Expression):
    size: Optional[Expression]      # puede ser None para []
    base: Expression                # tipo base

@dataclass
class FuncType(Expression):
    return_type: Expression
    params: List["Param"] = field(default_factory=list)


# =====================================================================
# Literales
# =====================================================================
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
# Expresiones
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

@dataclass
class FuncCall(Expression):
    name: str
    args: List[Expression] = field(default_factory=list)

@dataclass
class Assign(Expression):   # usado en parser: Assign(p.lval, p.expr1)
    target: Expression
    value : Expression


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
class Var(Location):   # usado en parser: Var(p.ID)
    pass

@dataclass
class ArrayLoc(Location):
    index: Expression

@dataclass
class ArrayAccess(Expression):   # acceso a arreglos
    array: Expression
    index: Expression


# =====================================================================
# Declaraciones
# =====================================================================
@dataclass
class ArrayDecl(Declaration):
    name : str
    type : Expression
    dims : List[Expression] = field(default_factory=list)

@dataclass
class FuncDecl(Declaration):
    name   : str
    type   : FuncType
    body   : List[Statement] = field(default_factory=list)

@dataclass
class Param(Declaration):
    name : str
    type : Expression


# =====================================================================
# Sentencias de control de flujo
# =====================================================================
@dataclass
class IfStmt(Statement):
    condition : Expression
    then_body : Statement
    else_body : Optional[Statement] = None

@dataclass
class WhileStmt(Statement):
    condition: Expression
    body     : Statement

@dataclass
class DoWhileStmt(Statement):
    body     : Statement
    condition: Expression

@dataclass
class ForStmt(Statement):
    init      : Optional[Statement]
    condition : Optional[Expression]
    step      : Optional[Statement]
    body      : Statement

@dataclass
class BlockStmt(Statement):
    body : List[Statement] = field(default_factory=list)


# =====================================================================
# Sentencias adicionales
# =====================================================================
@dataclass
class ReturnStmt(Statement):
    value : Optional[Expression] = None

@dataclass
class PrintStmt(Statement):
    args : List[Expression] = field(default_factory=list)

@dataclass
class Assignment(Statement):
    target: Location
    value : Expression
