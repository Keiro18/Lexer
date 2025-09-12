from dataclasses import dataclass, field
from multimethod import multimeta
from typing import List, Union, Optional

# =====================================================================
# Clases base
# =====================================================================
class Visitor(metaclass=multimeta):
    def visit(self, node, *args, **kwargs):
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, *args, **kwargs)

    def generic_visit(self, node, *args, **kwargs):
        raise NotImplementedError(f"No visit_{node.__class__.__name__} method")


@dataclass
class Node:
    def accept(self, v: Visitor, *args, **kwargs):
        return v.visit(self, *args, **kwargs)

    def pretty(self, level: int = 0) -> str:
        return " " * level + repr(self)


@dataclass
class Statement(Node):
    def pretty(self, level: int = 0) -> str:
        return " " * level + f"Statement()"


@dataclass
class Expression(Node):
    def pretty(self, level: int = 0) -> str:
        return " " * level + f"Expression()"


# =====================================================================
# Definiciones de alto nivel
# =====================================================================
@dataclass
class Program(Statement):
    body: List[Statement] = field(default_factory=list)

    def pretty(self, level=0):
        return "Program:\n" + "\n".join(stmt.pretty(level + 2) for stmt in self.body)


@dataclass
class Declaration(Statement):
    def pretty(self, level=0):
        return " " * level + f"Declaration()"


@dataclass
class Decl(Declaration):
    name: str
    type: Expression
    value: Optional[Expression] = None

    def pretty(self, level=0):
        return (
            " " * level
            + f"Decl(name={self.name}, type={self.type.pretty()}, value={self.value.pretty() if self.value else None})"
        )


# =====================================================================
# Tipos
# =====================================================================
@dataclass
class Type(Expression):
    name: str

    def pretty(self, level=0):
        return " " * level + f"Type({self.name})"


@dataclass
class ArrayType(Expression):
    size: Optional[Expression]
    base: Expression

    def pretty(self, level=0):
        return " " * level + f"ArrayType(size={self.size.pretty() if self.size else None}, base={self.base.pretty()})"


@dataclass
class FuncType(Expression):
    return_type: Expression
    params: List["Param"] = field(default_factory=list)

    def pretty(self, level=0):
        params_str = ", ".join(p.pretty() for p in self.params)
        return " " * level + f"FuncType(return={self.return_type.pretty()}, params=[{params_str}])"


# =====================================================================
# Literales
# =====================================================================
@dataclass
class Literal(Expression):
    value: Union[int, float, str, bool]
    type: str = None

    def pretty(self, level=0):
        return " " * level + f"{self.type.capitalize()}({self.value})"


@dataclass
class Integer(Literal):
    value: int
    def __post_init__(self):
        assert isinstance(self.value, int)
        self.type = "integer"


@dataclass
class Float(Literal):
    value: float
    def __post_init__(self):
        assert isinstance(self.value, float)
        self.type = "float"


@dataclass
class Boolean(Literal):
    value: bool
    def __post_init__(self):
        assert isinstance(self.value, bool)
        self.type = "boolean"


@dataclass
class Char(Literal):
    value: str
    def __post_init__(self):
        assert isinstance(self.value, str) and len(self.value) == 1
        self.type = "char"


@dataclass
class String(Literal):
    value: str
    def __post_init__(self):
        assert isinstance(self.value, str)
        self.type = "string"


# =====================================================================
# Expresiones
# =====================================================================
@dataclass
class BinOper(Expression):
    oper: str
    left: Expression
    right: Expression

    def pretty(self, level=0):
        return (
            " " * level
            + f"BinOper({self.oper}, left={self.left.pretty()}, right={self.right.pretty()})"
        )


@dataclass
class UnaryOper(Expression):
    oper: str
    expr: Expression

    def pretty(self, level=0):
        return " " * level + f"UnaryOper({self.oper}, expr={self.expr.pretty()})"


@dataclass
class PreInc(Expression):
    expr: Expression

    def pretty(self, level=0):
        return " " * level + f"PreInc({self.expr.pretty()})"


@dataclass
class PreDec(Expression):
    expr: Expression

    def pretty(self, level=0):
        return " " * level + f"PreDec({self.expr.pretty()})"


@dataclass
class PostInc(Expression):
    expr: Expression

    def pretty(self, level=0):
        return " " * level + f"PostInc({self.expr.pretty()})"


@dataclass
class PostDec(Expression):
    expr: Expression

    def pretty(self, level=0):
        return " " * level + f"PostDec({self.expr.pretty()})"


@dataclass
class FuncCall(Expression):
    name: str
    args: List[Expression] = field(default_factory=list)

    def pretty(self, level=0):
        args_str = ", ".join(arg.pretty() for arg in self.args)
        return " " * level + f"FuncCall({self.name}, args=[{args_str}])"


@dataclass
class Assign(Expression):
    target: Expression
    value: Expression

    def pretty(self, level=0):
        return (
            " " * level
            + f"Assign(target={self.target.pretty()}, value={self.value.pretty()})"
        )


# =====================================================================
# Ubicaciones
# =====================================================================
@dataclass
class Location(Expression):
    name: str

    def pretty(self, level=0):
        return " " * level + f"Location({self.name})"


@dataclass
class VarLoc(Location):
    def pretty(self, level=0):
        return " " * level + f"VarLoc({self.name})"


@dataclass
class Var(Location):
    def pretty(self, level=0):
        return " " * level + f"Var({self.name})"


@dataclass
class ArrayLoc(Location):
    index: Expression

    def pretty(self, level=0):
        return " " * level + f"ArrayLoc({self.name}, index={self.index.pretty()})"


@dataclass
class ArrayAccess(Expression):
    array: Expression
    index: Expression

    def pretty(self, level=0):
        return " " * level + f"ArrayAccess(array={self.array.pretty()}, index={self.index.pretty()})"


# =====================================================================
# Declaraciones
# =====================================================================
@dataclass
class ArrayDecl(Declaration):
    name: str
    type: Expression
    dims: List[Expression] = field(default_factory=list)

    def pretty(self, level=0):
        dims_str = ", ".join(d.pretty() for d in self.dims)
        return " " * level + f"ArrayDecl({self.name}, type={self.type.pretty()}, dims=[{dims_str}])"


@dataclass
class FuncDecl(Declaration):
    name: str
    type: FuncType
    body: List[Statement] = field(default_factory=list)

    def pretty(self, level=0):
        body_str = "\n".join(stmt.pretty(level + 2) for stmt in self.body)
        return " " * level + f"FuncDecl({self.name}, type={self.type.pretty()})\n{body_str}"


@dataclass
class Param(Declaration):
    name: str
    type: Expression

    def pretty(self, level=0):
        return " " * level + f"Param({self.name}, type={self.type.pretty()})"


# =====================================================================
# Sentencias de control de flujo
# =====================================================================
@dataclass
class IfStmt(Statement):
    condition: Expression
    then_body: Statement
    else_body: Optional[Statement] = None

    def pretty(self, level=0):
        result = " " * level + f"IfStmt(condition={self.condition.pretty()})\n"
        result += self.then_body.pretty(level + 2)
        if self.else_body:
            result += "\n" + " " * level + "Else:\n" + self.else_body.pretty(level + 2)
        return result


@dataclass
class WhileStmt(Statement):
    condition: Expression
    body: Statement

    def pretty(self, level=0):
        return (
            " " * level
            + f"WhileStmt(condition={self.condition.pretty()})\n{self.body.pretty(level+2)}"
        )


@dataclass
class DoWhileStmt(Statement):
    body: Statement
    condition: Expression

    def pretty(self, level=0):
        return (
            " " * level
            + f"DoWhileStmt(condition={self.condition.pretty()})\n{self.body.pretty(level+2)}"
        )


@dataclass
class ForStmt(Statement):
    init: Optional[Statement]
    condition: Optional[Expression]
    step: Optional[Statement]
    body: Statement

    def pretty(self, level=0):
        return (
            " " * level
            + f"ForStmt(init={self.init.pretty() if self.init else None}, "
              f"condition={self.condition.pretty() if self.condition else None}, "
              f"step={self.step.pretty() if self.step else None})\n"
              f"{self.body.pretty(level+2)}"
        )


@dataclass
class BlockStmt(Statement):
    body: List[Statement] = field(default_factory=list)

    def pretty(self, level=0):
        return " " * level + "Block:\n" + "\n".join(stmt.pretty(level + 2) for stmt in self.body)


# =====================================================================
# Sentencias adicionales
# =====================================================================
@dataclass
class ReturnStmt(Statement):
    value: Optional[Expression] = None

    def pretty(self, level=0):
        return " " * level + f"Return({self.value.pretty() if self.value else None})"


@dataclass
class PrintStmt(Statement):
    args: List[Expression] = field(default_factory=list)

    def pretty(self, level=0):
        args_str = ", ".join(arg.pretty() for arg in self.args)
        return " " * level + f"Print({args_str})"


@dataclass
class Assignment(Statement):
    target: Location
    value: Expression

    def pretty(self, level=0):
        return (
            " " * level
            + f"Assignment(target={self.target.pretty()}, value={self.value.pretty()})"
        )
# =====================================================================