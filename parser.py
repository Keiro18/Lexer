import logging
import sly
from rich import print

from lexer import Lexer
from errors import error, errors_detected
from model import *  # Todas las clases de nodos (Program, WhileStmt, ...)
from model import ASTPrinter


def _L(node, lineno=None):
    """Adjunta lineno al nodo AST si se proporciona."""
    if lineno is not None:
        node.lineno = lineno
    return node


def first_lineno(p):
    """Devuelve el primer atributo 'lineno' disponible en la pslice `p`. Si no hay ninguno, devuelve 0."""
    for i in range(len(p)):
        sym = p[i]
        if hasattr(sym, "lineno"):
            return sym.lineno
    return 0


class Parser(sly.Parser):
    log = logging.getLogger()
    log.setLevel(logging.ERROR)
    debugfile = "grammar.txt"

    tokens = Lexer.tokens

    # ------------------------------
    # Programa principal
    # ------------------------------
    @_("decl_list")
    def prog(self, p):
        lineno = first_lineno(p)
        prog = _L(Program(body=p.decl_list), lineno)
        setattr(prog, "decls", prog.body)  # compatibilidad con pruebas antiguas
        return prog

    # ------------------------------
    # Declaraciones
    # ------------------------------
    @_("decl decl_list")
    def decl_list(self, p):
        if p.decl is None:
            return p.decl_list
        if isinstance(p.decl, list):
            return p.decl + p.decl_list
        return [p.decl] + p.decl_list

    @_("empty")
    def decl_list(self, p):
        return []

    @_("stmt")
    def decl(self, p):
        return p.stmt

    # ------------------------------
    # Statements
    # ------------------------------
    @_("stmt_list")
    def opt_stmt_list(self, p):
        return p.stmt_list

    @_("empty")
    def opt_stmt_list(self, p):
        return []

    @_("stmt stmt_list")
    def stmt_list(self, p):
        return [p.stmt] + p.stmt_list

    @_("stmt")
    def stmt_list(self, p):
        return [p.stmt]

    @_("open_stmt")
    @_("closed_stmt")
    def stmt(self, p):
        return p[0]

    @_("if_stmt_closed")
    @_("for_stmt_closed")
    @_("while_stmt")
    @_("dowhile_stmt")
    @_("simple_stmt")
    def closed_stmt(self, p):
        return p[0]

    @_("if_stmt_open",
       "for_stmt_open")
    def open_stmt(self, p):
        return p[0]

    # ------------------------------
    # While / Do-While
    # ------------------------------
    @_("WHILE '(' assignment ')' stmt")
    def while_stmt(self, p):
        lineno = first_lineno(p)
        return _L(WhileStmt(condition=p.assignment, body=p.stmt), lineno)

    @_("DO stmt WHILE '(' assignment ')' ';'")
    def dowhile_stmt(self, p):
        lineno = first_lineno(p)
        return _L(DoWhileStmt(body=p.stmt, condition=p.assignment), lineno)

    # ------------------------------
    # Simple statements
    # ------------------------------
    @_("print_stmt")
    @_("return_stmt")
    @_("block_stmt")
    @_("decl")
    @_("assignment ';'")
    def simple_stmt(self, p):
        return p[0]

    @_("PRINT opt_expr_list ';'")
    def print_stmt(self, p):
        lineno = first_lineno(p)
        return _L(PrintStmt(args=p.opt_expr_list), lineno)

    @_("RETURN opt_expr ';'")
    def return_stmt(self, p):
        lineno = first_lineno(p)
        return _L(ReturnStmt(value=p.opt_expr), lineno)

    @_("'{' opt_stmt_list '}'")
    def block_stmt(self, p):
        lineno = first_lineno(p)
        return _L(BlockStmt(body=p.opt_stmt_list), lineno)

    # ------------------------------
    # EXPRESSIONS
    # ------------------------------
    @_("lval '=' assignment")
    @_("logical_or")
    def assignment(self, p):
        lineno = first_lineno(p)
        if hasattr(p, "lval") and hasattr(p, "assignment"):
            return _L(Assign(target=p.lval, value=p.assignment), lineno)
        return p.logical_or

    @_("logical_or LOR logical_and")
    @_("logical_and")
    def logical_or(self, p):
        lineno = first_lineno(p)
        if hasattr(p, "logical_or") and hasattr(p, "logical_and"):
            return _L(BinOper(oper="||", left=p.logical_or, right=p.logical_and), lineno)
        return p.logical_and

    @_("logical_and LAND equality")
    @_("equality")
    def logical_and(self, p):
        lineno = first_lineno(p)
        if hasattr(p, "logical_and") and hasattr(p, "equality"):
            return _L(BinOper(oper="&&", left=p.logical_and, right=p.equality), lineno)
        return p.equality

    @_("equality EQ relational")
    @_("equality NE relational")
    @_("relational")
    def equality(self, p):
        lineno = first_lineno(p)
        if hasattr(p, "equality") and hasattr(p, "relational"):
            op = "==" if hasattr(p, "EQ") else "!="
            return _L(BinOper(oper=op, left=p.equality, right=p.relational), lineno)
        return p.relational

    @_("relational LT additive")
    @_("relational LE additive")
    @_("relational GT additive")
    @_("relational GE additive")
    @_("additive")
    def relational(self, p):
        lineno = first_lineno(p)
        if hasattr(p, "relational") and hasattr(p, "additive"):
            if hasattr(p, "LT"):
                op = "<"
            elif hasattr(p, "LE"):
                op = "<="
            elif hasattr(p, "GT"):
                op = ">"
            else:
                op = ">="
            return _L(BinOper(oper=op, left=p.relational, right=p.additive), lineno)
        return p.additive

    @_("additive '+' multiplicative")
    @_("additive '-' multiplicative")
    @_("multiplicative")
    def additive(self, p):
        lineno = first_lineno(p)
        if hasattr(p, "additive") and hasattr(p, "multiplicative"):
            op = p[1]
            return _L(BinOper(oper=op, left=p.additive, right=p.multiplicative), lineno)
        return p.multiplicative

    @_("multiplicative '*' unary")
    @_("multiplicative '/' unary")
    @_("multiplicative '%' unary")
    @_("unary")
    def multiplicative(self, p):
        lineno = first_lineno(p)
        if hasattr(p, "multiplicative") and hasattr(p, "unary"):
            op = p[1]
            return _L(BinOper(oper=op, left=p.multiplicative, right=p.unary), lineno)
        return p.unary

    @_("INC unary")
    @_("DEC unary")
    @_("NOT unary")
    @_("'-' unary")
    @_("postfix")
    def unary(self, p):
        lineno = first_lineno(p)
        if hasattr(p, "INC"):
            return _L(PreInc(expr=p.unary), lineno)
        if hasattr(p, "DEC"):
            return _L(PreDec(expr=p.unary), lineno)
        if hasattr(p, "NOT"):
            return _L(UnaryOper(oper="!", expr=p.unary), lineno)
        if hasattr(p, "'-'"):
            return _L(UnaryOper(oper="-", expr=p.unary), lineno)
        return p.postfix

    @_("postfix INC")
    def postfix(self, p):
        lineno = first_lineno(p)
        return _L(PostInc(expr=p.postfix), lineno)

    @_("postfix DEC")
    def postfix(self, p):
        lineno = first_lineno(p)
        return _L(PostDec(expr=p.postfix), lineno)

    @_("primary")
    def postfix(self, p):
        return p.primary

    @_("'(' assignment ')'")
    @_("ID index")
    @_("ID")
    @_("INT_LITERAL")
    @_("FLOAT_LITERAL")
    @_("CHAR_LITERAL")
    @_("STRING_LITERAL")
    @_("TRUE")
    @_("FALSE")
    def primary(self, p):
        lineno = first_lineno(p)
        if hasattr(p, "assignment"):
            return p.assignment
        if hasattr(p, "ID") and hasattr(p, "index"):
            return _L(ArrayAccess(array=Var(p.ID), index=p.index), lineno)
        if hasattr(p, "ID") and not hasattr(p, "index"):
            return _L(Var(p.ID), lineno)
        if hasattr(p, "INT_LITERAL"):
            return _L(Integer(value=int(p.INT_LITERAL)), lineno)
        if hasattr(p, "FLOAT_LITERAL"):
            return _L(Float(value=float(p.FLOAT_LITERAL)), lineno)
        if hasattr(p, "CHAR_LITERAL"):
            s = p.CHAR_LITERAL.strip("'")
            return _L(Char(value=s), lineno)
        if hasattr(p, "STRING_LITERAL"):
            s = p.STRING_LITERAL.strip('"')
            return _L(String(value=s), lineno)
        if hasattr(p, "TRUE"):
            return _L(Boolean(value=True), lineno)
        if hasattr(p, "FALSE"):
            return _L(Boolean(value=False), lineno)
        return None

    @_("'[' assignment ']'")
    def index(self, p):
        return p.assignment

    @_('ID')
    def lval(self, p):
        lineno = first_lineno(p)
        return _L(VarLoc(p.ID), lineno)

    @_('ID "[" assignment "]"')
    def lval(self, p):
        lineno = first_lineno(p)
        return _L(ArrayLoc(name=p.ID, index=p.assignment), lineno)

    # ------------------------------
    # Stubs (if/for/expr opcional)
    # ------------------------------
    @_("empty")
    def if_stmt_closed(self, p): return None

    @_("empty")
    def if_stmt_open(self, p): return None

    @_("empty")
    def for_stmt_closed(self, p): return None

    @_("empty")
    def for_stmt_open(self, p): return None

    @_("empty")
    def opt_expr(self, p): return None

    @_("empty")
    def opt_expr_list(self, p): return []

    # ------------------------------
    # Helpers
    # ------------------------------
    @_("")
    def empty(self, p): return None

    def error(self, p):
        lineno = p.lineno if p else "EOF"
        value = repr(p.value) if p else "EOF"
        error(f"Syntax error at {value}", lineno)


# ------------------------------
# Funciones auxiliares
# ------------------------------
def ast_to_dict(node):
    if isinstance(node, list):
        return [ast_to_dict(item) for item in node]
    elif hasattr(node, "__dict__"):
        return {key: ast_to_dict(value) for key, value in node.__dict__.items()}
    else:
        return node


def parse(txt):
    l = Lexer()
    p = Parser()
    return p.parse(l.tokenize(txt))


def debug_tokens(source):
    l = Lexer()
    for t in l.tokenize(source):
        print(t)


if __name__ == "__main__":
    # prueba rápida
    src = "do { x = x + 1; } while (x < 10);"
    print("=== TOKENS ===")
    debug_tokens(src)
    print("\n=== AST ===")
    ast = parse(src)
    if ast:
        # Mostrar AST en texto
        print(ast.pretty())

        # Generar grafo con Graphviz
        dot = ASTPrinter.render(ast)
        dot.render("ast_output", format="png", cleanup=True)
        print("\nAST exportado como ast_output.png")
    else:
        print("No se generó AST (error de sintaxis)")
