# printer.py
from rich.tree import Tree
from rich.console import Console
from multimethod import multimethod

from model import *  # tus clases del AST


class ASTPrinter:
    def __init__(self):
        self.console = Console()

    def print(self, node, label="root"):
        tree = self.visit(node, label)
        self.console.print(tree)

    # ---- casos genéricos ----
    @multimethod
    def visit(self, node: list, label: str) -> Tree:
        t = Tree(f"{label}: list")
        for i, item in enumerate(node):
            t.add(self.visit(item, f"[{i}]"))
        return t

    @multimethod
    def visit(self, node: object, label: str) -> Tree:
        # fallback: imprime nombre de clase y atributos
        t = Tree(f"{label}: {node.__class__.__name__}")
        if hasattr(node, "__dict__"):
            for key, value in node.__dict__.items():
                if value is not None:
                    t.add(self.visit(value, key))
        else:
            t.add(str(node))
        return t

    # ---- casos concretos ----
    @multimethod
    def visit(self, node: Integer, label: str) -> Tree:
        return Tree(f"{label}: Integer({node.value})")

    @multimethod
    def visit(self, node: Float, label: str) -> Tree:
        return Tree(f"{label}: Float({node.value})")

    @multimethod
    def visit(self, node: String, label: str) -> Tree:
        return Tree(f"{label}: String({node.value})")

    @multimethod
    def visit(self, node: Char, label: str) -> Tree:
        return Tree(f"{label}: Char('{node.value}')")

    @multimethod
    def visit(self, node: Boolean, label: str) -> Tree:
        return Tree(f"{label}: Boolean({node.value})")

    @multimethod
    def visit(self, node: Var, label: str) -> Tree:
        return Tree(f"{label}: Var({node.name})")