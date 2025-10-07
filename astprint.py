# astprint.py
# Impresión visual del AST usando Graphviz
# Compatible con el parser de B-Minor

from graphviz import Digraph
from rich import print
from rich.tree import Tree
from rich.console import Console
import sys
import os

try:
    from bminor_ast import *
except ImportError:
    from model import *
    
class ASTPrinter:
    node_defaults = {
        'shape': 'box',
        'color': 'deepskyblue',
        'style': 'filled'
    }
    edge_defaults = {
        'arrowhead': 'none'
    }

    def __init__(self):
        self.dot = Digraph('AST')
        self.dot.attr('node', **self.node_defaults)
        self.dot.attr('edge', **self.edge_defaults)
        self._seq = 0

    @property
    def name(self):
        self._seq += 1
        return f'n{self._seq:02d}'

    @classmethod
    def render(cls, n):
        dot = cls()
        dot.visit(n)
        return dot.dot

    # =====================================================================
    # Método visit principal con dispatch manual
    # =====================================================================
    
    def visit(self, n):
        method_name = f'visit_{type(n).__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(n)
    
    def generic_visit(self, n):
        name = self.name
        self.dot.node(name, label=f'{type(n).__name__}')
        return name

    # =====================================================================
    # Nodos Estructurales y Declaraciones
    # =====================================================================

    def visit_Program(self, n):
        name = self.name
        self.dot.node(name, label='Program')
        for stmt in n.body:
            self.dot.edge(name, self.visit(stmt))
        return name

    def visit_VarDecl(self, n):
        name = self.name
        type_str = self._get_type_string(n.type)
        self.dot.node(name, label=f'VarDecl\n{n.name}: {type_str}')
        if n.value:
            self.dot.edge(name, self.visit(n.value), label='value')
        return name

    def visit_VarDeclInit(self, n):
        name = self.name
        type_str = self._get_type_string(n.typ)
        self.dot.node(name, label=f'VarDeclInit\n{n.name}: {type_str}')
        
        if isinstance(n.init, list):
            init_name = self.name
            self.dot.node(init_name, label='InitList')
            self.dot.edge(name, init_name)
            for item in n.init:
                self.dot.edge(init_name, self.visit(item))
        else:
            self.dot.edge(name, self.visit(n.init), label='init')
        return name

    def visit_FuncDecl(self, n):
        name = self.name
        
        # Extraer información del tipo de función
        if n.type_func:
            param_names = ', '.join([p.name for p in n.type_func.params])
            ret_type = self._get_type_string(n.type_func.ret_type)
        else:
            param_names = ''
            ret_type = 'unknown'
        
        self.dot.node(name, label=f'FuncDecl\n{n.name}({param_names})\n→ {ret_type}')
        
        # Visualizar el cuerpo si existe
        if n.body:
            body_name = self.name
            self.dot.node(body_name, label='Body')
            self.dot.edge(name, body_name)
            for stmt in n.body:
                self.dot.edge(body_name, self.visit(stmt))
        return name

    def visit_Block(self, n):
        name = self.name
        self.dot.node(name, label='Block')
        for stmt in n.body:
            self.dot.edge(name, self.visit(stmt))
        return name

    # =====================================================================
    # Nodos de Tipos
    # =====================================================================

    def visit_SimpleType(self, n):
        name = self.name
        self.dot.node(name, label=f'Type: {n.name}')
        return name

    def visit_ArrayType(self, n):
        name = self.name
        self.dot.node(name, label='ArrayType')
        if n.size:
            self.dot.edge(name, self.visit(n.size), label='size')
        self.dot.edge(name, self.visit(n.elem_type), label='elem')
        return name

    def visit_FuncType(self, n):
        name = self.name
        self.dot.node(name, label='FuncType')
        self.dot.edge(name, self.visit(n.ret_type), label='return')
        for param in n.params:
            self.dot.edge(name, self.visit(param), label='param')
        return name

    def visit_Param(self, n):
        name = self.name
        type_str = self._get_type_string(n.typ)
        self.dot.node(name, label=f'Param\n{n.name}: {type_str}')
        return name

    # =====================================================================
    # Nodos de Sentencias de Control
    # =====================================================================

    def visit_IfStmt(self, n):
        name = self.name
        self.dot.node(name, label='If')
        if n.cond:
            self.dot.edge(name, self.visit(n.cond), label='cond')
        self.dot.edge(name, self.visit(n.then_branch), label='then')
        if n.else_branch:
            self.dot.edge(name, self.visit(n.else_branch), label='else')
        return name

    def visit_WhileStmt(self, n):
        name = self.name
        self.dot.node(name, label='While')
        self.dot.edge(name, self.visit(n.cond), label='cond')
        self.dot.edge(name, self.visit(n.body), label='body')
        return name

    def visit_DoWhileStmt(self, n):
        name = self.name
        self.dot.node(name, label='DoWhile')
        self.dot.edge(name, self.visit(n.body), label='body')
        self.dot.edge(name, self.visit(n.cond), label='cond')
        return name

    def visit_ForStmt(self, n):
        name = self.name
        self.dot.node(name, label='For')
        if n.init:
            self.dot.edge(name, self.visit(n.init), label='init')
        if n.cond:
            self.dot.edge(name, self.visit(n.cond), label='cond')
        if n.step:
            self.dot.edge(name, self.visit(n.step), label='step')
        self.dot.edge(name, self.visit(n.body), label='body')
        return name

    def visit_ReturnStmt(self, n):
        name = self.name
        self.dot.node(name, label='Return')
        if n.expr:
            self.dot.edge(name, self.visit(n.expr))
        return name

    def visit_PrintStmt(self, n):
        name = self.name
        self.dot.node(name, label='Print')
        if isinstance(n.expr, list):
            for item in n.expr:
                self.dot.edge(name, self.visit(item))
        elif n.expr:
            self.dot.edge(name, self.visit(n.expr))
        return name

    # =====================================================================
    # Nodos de Expresiones
    # =====================================================================

    def visit_BinOper(self, n):
        name = self.name
        self.dot.node(name, label=f'{n.oper}', shape='circle', color='lightcoral')
        self.dot.edge(name, self.visit(n.left))
        if n.right:
            self.dot.edge(name, self.visit(n.right))
        return name

    def visit_UnaryOper(self, n):
        name = self.name
        self.dot.node(name, label=f'{n.oper}', shape='circle', color='lightcoral')
        self.dot.edge(name, self.visit(n.expr))
        return name

    def visit_Assign(self, n):
        name = self.name
        self.dot.node(name, label='=', shape='circle', color='gold')
        self.dot.edge(name, self.visit(n.left), label='lval')
        self.dot.edge(name, self.visit(n.right), label='rval')
        return name

    def visit_Call(self, n):
        name = self.name
        self.dot.node(name, label='Call', color='mediumpurple')
        self.dot.edge(name, self.visit(n.func), label='func')
        for i, arg in enumerate(n.args):
            self.dot.edge(name, self.visit(arg), label=f'arg{i}')
        return name

    def visit_ArrayAccess(self, n):
        name = self.name
        self.dot.node(name, label='[]', shape='circle', color='lightgreen')
        self.dot.edge(name, self.visit(n.array), label='array')
        self.dot.edge(name, self.visit(n.index), label='index')
        return name

    def visit_PreInc(self, n):
        name = self.name
        self.dot.node(name, label='++', shape='circle', color='lightcoral')
        self.dot.edge(name, self.visit(n.expr))
        return name

    def visit_PreDec(self, n):
        name = self.name
        self.dot.node(name, label='--', shape='circle', color='lightcoral')
        self.dot.edge(name, self.visit(n.expr))
        return name

    # =====================================================================
    # Nodos Hoja (Literales e Identificadores)
    # =====================================================================

    def visit_Integer(self, n):
        name = self.name
        self.dot.node(name, label=f'{n.value}', color='lightyellow')
        return name

    def visit_Float(self, n):
        name = self.name
        self.dot.node(name, label=f'{n.value}', color='lightyellow')
        return name

    def visit_Boolean(self, n):
        name = self.name
        self.dot.node(name, label=f'{n.value}', color='lightpink')
        return name

    def visit_Char(self, n):
        name = self.name
        self.dot.node(name, label=f"'{n.value}'", color='lightyellow')
        return name

    def visit_String(self, n):
        name = self.name
        # Limitar la longitud de strings largos
        display_val = n.value if len(n.value) < 20 else n.value[:17] + '...'
        self.dot.node(name, label=f'"{display_val}"', color='lightyellow')
        return name

    def visit_Identifier(self, n):
        name = self.name
        self.dot.node(name, label=f'{n.name}', color='lightblue')
        return name

    # =====================================================================
    # Métodos Auxiliares
    # =====================================================================

    def _get_type_string(self, typ):
        """Obtiene una representación de string del tipo"""
        if isinstance(typ, SimpleType):
            return typ.name
        elif isinstance(typ, ArrayType):
            elem_str = self._get_type_string(typ.elem_type)
            return f'array[{typ.size if typ.size else ""}] {elem_str}'
        elif isinstance(typ, FuncType):
            ret_str = self._get_type_string(typ.ret_type)
            return f'function → {ret_str}'
        else:
            return str(typ)


# =====================================================================
# Impresión en consola con Rich Tree
# =====================================================================

class ASTConsolePrinter:
    """Imprime el AST en consola usando Rich Tree"""
    
    @staticmethod
    def print_tree(node, tree=None, is_root=True):
        """Imprime el AST como un árbol en consola"""
        if is_root:
            tree = Tree("[bold cyan]AST - Abstract Syntax Tree[/bold cyan]")
        
        if isinstance(node, Program):
            branch = tree.add("[bold green]Program[/bold green]")
            for decl in node.body:
                ASTConsolePrinter.print_tree(decl, branch, False)
        
        elif isinstance(node, VarDecl):
            type_str = ASTConsolePrinter._get_type_str(node.type)
            label = f"[yellow]VarDecl[/yellow] [cyan]{node.name}[/cyan]: {type_str}"
            branch = tree.add(label)
            if node.value:
                value_branch = branch.add("[dim]value:[/dim]")
                ASTConsolePrinter.print_tree(node.value, value_branch, False)
        
        elif isinstance(node, VarDeclInit):
            type_str = ASTConsolePrinter._get_type_str(node.typ)
            label = f"[yellow]VarDeclInit[/yellow] [cyan]{node.name}[/cyan]: {type_str}"
            branch = tree.add(label)
            if isinstance(node.init, list):
                init_branch = branch.add("[dim]init list:[/dim]")
                for item in node.init:
                    ASTConsolePrinter.print_tree(item, init_branch, False)
            else:
                init_branch = branch.add("[dim]init:[/dim]")
                ASTConsolePrinter.print_tree(node.init, init_branch, False)
        
        elif isinstance(node, FuncDecl):
            if node.type_func:
                params = ', '.join([p.name for p in node.type_func.params])
                ret_type = ASTConsolePrinter._get_type_str(node.type_func.ret_type)
            else:
                params = ''
                ret_type = 'unknown'
            label = f"[yellow]FuncDecl[/yellow] [cyan]{node.name}[/cyan]({params}) → {ret_type}"
            branch = tree.add(label)
            if node.body:
                body_branch = branch.add("[dim]body:[/dim]")
                for stmt in node.body:
                    ASTConsolePrinter.print_tree(stmt, body_branch, False)
        
        elif isinstance(node, Block):
            branch = tree.add("[magenta]Block[/magenta]")
            for stmt in node.body:
                ASTConsolePrinter.print_tree(stmt, branch, False)
        
        elif isinstance(node, IfStmt):
            branch = tree.add("[magenta]If[/magenta]")
            if node.cond:
                cond_branch = branch.add("[dim]condition:[/dim]")
                ASTConsolePrinter.print_tree(node.cond, cond_branch, False)
            then_branch = branch.add("[dim]then:[/dim]")
            ASTConsolePrinter.print_tree(node.then_branch, then_branch, False)
            if node.else_branch:
                else_branch = branch.add("[dim]else:[/dim]")
                ASTConsolePrinter.print_tree(node.else_branch, else_branch, False)
        
        elif isinstance(node, ForStmt):
            branch = tree.add("[magenta]For[/magenta]")
            if node.init:
                init_branch = branch.add("[dim]init:[/dim]")
                ASTConsolePrinter.print_tree(node.init, init_branch, False)
            if node.cond:
                cond_branch = branch.add("[dim]condition:[/dim]")
                ASTConsolePrinter.print_tree(node.cond, cond_branch, False)
            if node.step:
                step_branch = branch.add("[dim]step:[/dim]")
                ASTConsolePrinter.print_tree(node.step, step_branch, False)
            body_branch = branch.add("[dim]body:[/dim]")
            ASTConsolePrinter.print_tree(node.body, body_branch, False)
        
        elif isinstance(node, WhileStmt):
            branch = tree.add("[magenta]While[/magenta]")
            cond_branch = branch.add("[dim]condition:[/dim]")
            ASTConsolePrinter.print_tree(node.cond, cond_branch, False)
            body_branch = branch.add("[dim]body:[/dim]")
            ASTConsolePrinter.print_tree(node.body, body_branch, False)
        
        elif isinstance(node, DoWhileStmt):
            branch = tree.add("[magenta]DoWhile[/magenta]")
            body_branch = branch.add("[dim]body:[/dim]")
            ASTConsolePrinter.print_tree(node.body, body_branch, False)
            cond_branch = branch.add("[dim]condition:[/dim]")
            ASTConsolePrinter.print_tree(node.cond, cond_branch, False)
        
        elif isinstance(node, ReturnStmt):
            branch = tree.add("[magenta]Return[/magenta]")
            if node.expr:
                ASTConsolePrinter.print_tree(node.expr, branch, False)
        
        elif isinstance(node, PrintStmt):
            branch = tree.add("[magenta]Print[/magenta]")
            if isinstance(node.expr, list):
                for item in node.expr:
                    ASTConsolePrinter.print_tree(item, branch, False)
            elif node.expr:
                ASTConsolePrinter.print_tree(node.expr, branch, False)
        
        elif isinstance(node, Assign):
            branch = tree.add("[red]=[/red] [dim](assign)[/dim]")
            left_branch = branch.add("[dim]left:[/dim]")
            ASTConsolePrinter.print_tree(node.left, left_branch, False)
            right_branch = branch.add("[dim]right:[/dim]")
            ASTConsolePrinter.print_tree(node.right, right_branch, False)
        
        elif isinstance(node, BinOper):
            branch = tree.add(f"[red]{node.oper}[/red] [dim](binop)[/dim]")
            ASTConsolePrinter.print_tree(node.left, branch, False)
            if node.right:
                ASTConsolePrinter.print_tree(node.right, branch, False)
        
        elif isinstance(node, UnaryOper):
            branch = tree.add(f"[red]{node.oper}[/red] [dim](unary)[/dim]")
            ASTConsolePrinter.print_tree(node.expr, branch, False)
        
        elif isinstance(node, Call):
            branch = tree.add("[blue]Call[/blue]")
            func_branch = branch.add("[dim]function:[/dim]")
            ASTConsolePrinter.print_tree(node.func, func_branch, False)
            if node.args:
                args_branch = branch.add("[dim]arguments:[/dim]")
                for arg in node.args:
                    ASTConsolePrinter.print_tree(arg, args_branch, False)
        
        elif isinstance(node, ArrayAccess):
            branch = tree.add("[blue][][/blue] [dim](array access)[/dim]")
            array_branch = branch.add("[dim]array:[/dim]")
            ASTConsolePrinter.print_tree(node.array, array_branch, False)
            index_branch = branch.add("[dim]index:[/dim]")
            ASTConsolePrinter.print_tree(node.index, index_branch, False)
        
        elif isinstance(node, Identifier):
            tree.add(f"[cyan]{node.name}[/cyan] [dim](id)[/dim]")
        
        elif isinstance(node, Integer):
            tree.add(f"[green]{node.value}[/green] [dim](int)[/dim]")
        
        elif isinstance(node, Float):
            tree.add(f"[green]{node.value}[/green] [dim](float)[/dim]")
        
        elif isinstance(node, Boolean):
            tree.add(f"[green]{node.value}[/green] [dim](bool)[/dim]")
        
        elif isinstance(node, Char):
            tree.add(f"[green]'{node.value}'[/green] [dim](char)[/dim]")
        
        elif isinstance(node, String):
            display_val = node.value if len(node.value) < 30 else node.value[:27] + '...'
            tree.add(f'[green]"{display_val}"[/green] [dim](string)[/dim]')
        
        elif isinstance(node, SimpleType):
            tree.add(f"[yellow]{node.name}[/yellow] [dim](type)[/dim]")
        
        elif isinstance(node, ArrayType):
            size_str = "[]" if not node.size else f"[size]"
            branch = tree.add(f"[yellow]array{size_str}[/yellow] [dim](type)[/dim]")
            if node.size:
                size_branch = branch.add("[dim]size:[/dim]")
                ASTConsolePrinter.print_tree(node.size, size_branch, False)
            elem_branch = branch.add("[dim]element type:[/dim]")
            ASTConsolePrinter.print_tree(node.elem_type, elem_branch, False)
        
        elif isinstance(node, FuncType):
            branch = tree.add("[yellow]function type[/yellow]")
            ret_branch = branch.add("[dim]return type:[/dim]")
            ASTConsolePrinter.print_tree(node.ret_type, ret_branch, False)
            if node.params:
                params_branch = branch.add("[dim]parameters:[/dim]")
                for param in node.params:
                    ASTConsolePrinter.print_tree(param, params_branch, False)
        
        elif isinstance(node, Param):
            type_str = ASTConsolePrinter._get_type_str(node.typ)
            tree.add(f"[cyan]{node.name}[/cyan]: {type_str} [dim](param)[/dim]")
        
        elif isinstance(node, list):
            for item in node:
                ASTConsolePrinter.print_tree(item, tree, False)
        
        else:
            tree.add(f"[dim]{type(node).__name__}[/dim]")
        
        if is_root:
            return tree
    
    @staticmethod
    def _get_type_str(typ):
        """Obtiene representación string del tipo"""
        if isinstance(typ, SimpleType):
            return f"[yellow]{typ.name}[/yellow]"
        elif isinstance(typ, ArrayType):
            elem = ASTConsolePrinter._get_type_str(typ.elem_type)
            return f"[yellow]array[][/yellow] {elem}"
        elif isinstance(typ, FuncType):
            ret = ASTConsolePrinter._get_type_str(typ.ret_type)
            return f"[yellow]function[/yellow] → {ret}"
        else:
            return str(typ)


# =====================================================================
# Función Principal
# =====================================================================

def main():
    if len(sys.argv) != 2:
        print("[red]Uso:[/red] python astprint.py <archivo.bminor>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        from bminor_lexer import BMinorLexer
        from bminor_parser import BMinorParser

        # Leer el archivo
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()

        # Parsear
        lexer = BMinorLexer()
        parser = BMinorParser()
        ast = parser.parse(lexer.tokenize(text))

        if ast:
            console = Console()
            
            print("[green]✓[/green] Análisis sintáctico exitoso!\n")
            
            # Imprimir AST en consola con Rich Tree
            print("[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]")
            print("[bold cyan]           AST - Árbol de Sintaxis Abstracta          [/bold cyan]")
            print("[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]\n")
            
            tree = ASTConsolePrinter.print_tree(ast)
            console.print(tree)
            
            print("\n[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]\n")
            
            # Generar visualización Graphviz
            print(f"[cyan]Generando visualización gráfica del AST...[/cyan]\n")

            # Renderizar el AST
            dot = ASTPrinter.render(ast)

            # Guardar archivos de salida
            output_file = filename.rsplit('.', 1)[0]
            
            # Siempre guardar el archivo .dot
            dot_file = f"{output_file}.dot"
            with open(dot_file, 'w', encoding='utf-8') as f:
                f.write(str(dot))
            print(f"[green]✓[/green] Código Graphviz guardado en: [yellow]{dot_file}[/yellow]")
            print(f"[cyan]→[/cyan] Visualízalo en: https://dreampuf.github.io/GraphvizOnline/")
            
            # Intentar generar PDF (sin eliminar el .dot)
            try:
                dot.render(output_file, format='pdf', cleanup=False)
                print(f"[green]✓[/green] Gráfico PDF guardado en: [yellow]{output_file}.pdf[/yellow]")
            except Exception as e:
                print(f"[yellow]⚠[/yellow] No se pudo generar PDF: {e}")
                print(f"[yellow]→[/yellow] Instala Graphviz desde: https://graphviz.org/download/")
                print(f"[cyan]→[/cyan] Puedes usar el archivo .dot generado para visualización online")

        else:
            print("[red]✗[/red] Error: No se pudo construir el AST")
            sys.exit(1)

    except FileNotFoundError:
        print(f"[red]✗[/red] Error: No se encontró el archivo '{filename}'")
        sys.exit(1)
    except ImportError as e:
        print(f"[red]✗[/red] Error de importación: {e}")
        print("\nAsegúrate de tener instalados:")
        print("  - pip install graphviz")
        print("  - pip install rich")
        sys.exit(1)
    except Exception as e:
        print(f"[red]✗[/red] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()