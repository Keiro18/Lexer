from dataclasses import dataclass, field
from multimethod import multimeta
from typing import List, Union, Optional
from graphviz import Digraph

# =====================================================================
# Visitor base
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


# =====================================================================
# ASTPrinter usando el Visitor
# =====================================================================
class ASTPrinter(Visitor):
    node_defaults = {
        "shape": "box",
        "color": "deepskyblue",
        "style": "filled",
    }
    edge_defaults = {
        "arrowhead": "none",
    }

    def __init__(self):
        self.dot = Digraph("AST")
        self.dot.attr("node", **self.node_defaults)
        self.dot.attr("edge", **self.edge_defaults)
        self._seq = 0

    @property
    def name(self):
        self._seq += 1
        return f"n{self._seq:02d}"

    @classmethod
    def render(cls, n: Node):
        dot = cls()
        n.accept(dot)
        return dot.dot

    # ---- Visitors ----
    def visit_Program(self, n: "Program"):
        name = self.name
        self.dot.node(name, label="Program")
        for stmt in n.body:
            self.dot.edge(name, stmt.accept(self))
        return name

    def visit_Decl(self, n: "Decl"):
        name = self.name
        self.dot.node(name, label=f"Decl\n{n.name}:{n.type.pretty()}")
        if n.value:
            self.dot.edge(name, n.value.accept(self))
        return name

    def visit_BinOper(self, n: "BinOper"):
        name = self.name
        self.dot.node(name, label=f"{n.oper}", shape="circle")
        self.dot.edge(name, n.left.accept(self))
        self.dot.edge(name, n.right.accept(self))
        return name

    def visit_UnaryOper(self, n: "UnaryOper"):
        name = self.name
        self.dot.node(name, label=f"{n.oper}", shape="circle")
        self.dot.edge(name, n.expr.accept(self))
        return name

    def visit_Literal(self, n: "Literal"):
        name = self.name
        self.dot.node(name, label=f"{n.value}:{n.type}")
        return name

    # ---- Nodos concretos ----
    def visit_Integer(self, n: "Integer"):
        name = self.name
        self.dot.node(name, f"Integer({n.value})")
        return name

    def visit_Float(self, n: "Float"):
        name = self.name
        self.dot.node(name, f"Float({n.value})")
        return name

    def visit_Boolean(self, n: "Boolean"):
        name = self.name
        self.dot.node(name, f"Boolean({n.value})")
        return name

    def visit_Char(self, n: "Char"):
        name = self.name
        self.dot.node(name, f"Char({n.value})")
        return name

    def visit_String(self, n: "String"):
        name = self.name
        self.dot.node(name, f"String({n.value})")
        return name

    def visit_Type(self, n: "Type"):
        name = self.name
        self.dot.node(name, f"Type({n.name})")
        return name

    def visit_Var(self, n: "Var"):
        name = self.name
        self.dot.node(name, f"Var({n.name})")
        return name

    def visit_ArrayAccess(self, n: "ArrayAccess"):
        name = self.name
        self.dot.node(name, "ArrayAccess")
        self.dot.edge(name, n.array.accept(self))
        self.dot.edge(name, n.index.accept(self))
        return name


# =====================================================================
# Clases base de AST
# =====================================================================
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
# Variables y expresiones
# =====================================================================
@dataclass
class Var(Expression):
    name: str

    def pretty(self, level=0):
        return " " * level + f"Var({self.name})"


@dataclass
class ArrayAccess(Expression):
    array: Expression
    index: Expression

    def pretty(self, level=0):
        return " " * level + f"ArrayAccess(array={self.array.pretty()}, index={self.index.pretty()})"


@dataclass
class BinOper(Expression):
    oper: str
    left: Expression
    right: Expression

    def pretty(self, level=0):
        return (
            " " * level
            + f"BinOper({self.oper}, {self.left.pretty()}, {self.right.pretty()})"
        )


@dataclass
class UnaryOper(Expression):
    oper: str
    expr: Expression

    def pretty(self, level=0):
        return " " * level + f"UnaryOper({self.oper}, {self.expr.pretty()})"
