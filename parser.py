# parser.py
import logging
import sly
from rich import print

from lexer import Lexer
from errors import error, errors_detected
from model import *  # Todas las clases de nodos (Program, WhileStmt, ...)


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
        # Compatibilidad con pruebas antiguas que consultaban 'decls'
        setattr(prog, "decls", prog.body)
        return prog

    # ------------------------------
    # Declarations (tratamos statements como decls top-level)
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
    # Simple statements (incluye block_stmt)
    # ------------------------------
    @_("print_stmt")
    @_("return_stmt")
    @_("block_stmt")
    @_("decl")
    @_("assignment ';'")
    def simple_stmt(self, p):
        # p[0] será el nodo correspondiente (PrintStmt, ReturnStmt, BlockStmt, Assign...)
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
    # EXPRESSIONS: jerarquía de niveles
    # assignment -> logical_or -> logical_and -> equality -> relational
    # -> additive -> multiplicative -> unary -> postfix -> primary
    # ------------------------------

    # Top: assignment (lvalue '=' assignment) or logical_or
    @_("lval '=' assignment")
    @_("logical_or")
    def assignment(self, p):
        lineno = first_lineno(p)
        if hasattr(p, "lval") and hasattr(p, "assignment"):
            # p.lval es un Location (Var o ArrayAccess)
            return _L(Assign(target=p.lval, value=p.assignment), lineno)
        # fallback
        return p.logical_or

    # logical OR
    @_("logical_or LOR logical_and")
    @_("logical_and")
    def logical_or(self, p):
        lineno = first_lineno(p)
        if hasattr(p, "logical_or") and hasattr(p, "logical_and"):
            return _L(BinOper(oper="||", left=p.logical_or, right=p.logical_and), lineno)
        return p.logical_and

    # logical AND
    @_("logical_and LAND equality")
    @_("equality")
    def logical_and(self, p):
        lineno = first_lineno(p)
        if hasattr(p, "logical_and") and hasattr(p, "equality"):
            return _L(BinOper(oper="&&", left=p.logical_and, right=p.equality), lineno)
        return p.equality

    # equality: ==, !=
    @_("equality EQ relational")
    @_("equality NE relational")
    @_("relational")
    def equality(self, p):
        lineno = first_lineno(p)
        if hasattr(p, "equality") and hasattr(p, "relational"):
            op = "==" if hasattr(p, "EQ") else "!="
            return _L(BinOper(oper=op, left=p.equality, right=p.relational), lineno)
        return p.relational

    # relational: < <= > >=
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

    # additive: + -
    @_("additive '+' multiplicative")
    @_("additive '-' multiplicative")
    @_("multiplicative")
    def additive(self, p):
        lineno = first_lineno(p)
        if hasattr(p, "additive") and hasattr(p, "multiplicative"):
            op = p[1]  # '+' or '-'
            return _L(BinOper(oper=op, left=p.additive, right=p.multiplicative), lineno)
        return p.multiplicative

    # multiplicative: * / %
    @_("multiplicative '*' unary")
    @_("multiplicative '/' unary")
    @_("multiplicative '%' unary")
    @_("unary")
    def multiplicative(self, p):
        lineno = first_lineno(p)
        if hasattr(p, "multiplicative") and hasattr(p, "unary"):
            op = p[1]  # '*', '/', '%'
            return _L(BinOper(oper=op, left=p.multiplicative, right=p.unary), lineno)
        return p.unary

    # unary: prefix inc/dec, NOT, '-' or fallback to postfix
    @_("INC unary")
    @_("DEC unary")
    @_("NOT unary")
    @_("'-' unary")
    @_("postfix")
    def unary(self, p):
        lineno = first_lineno(p)
        # pre-inc / pre-dec
        if hasattr(p, "INC"):
            # pre-inc applied to the nested unary result
            return _L(PreInc(expr=p.unary), lineno)
        if hasattr(p, "DEC"):
            return _L(PreDec(expr=p.unary), lineno)
        # not
        if hasattr(p, "NOT"):
            # If you have UnaryOper use it; otherwise use UnaryOper with '!' operator
            return _L(UnaryOper(oper="!", expr=p.unary), lineno)
        # unary minus
        if hasattr(p, "'-'"):
            return _L(UnaryOper(oper="-", expr=p.unary), lineno)
        return p.postfix

    # postfix: primary (with possible chained INC/DEC)
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

    # primary: grouping, ID (optionally with index), literals, function call
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

        # grouping
        if hasattr(p, "assignment") and p.assignment is not None:
            return p.assignment

        # ID with index -> ArrayAccess
        if hasattr(p, "ID") and hasattr(p, "index"):
            return _L(ArrayAccess(array=Var(p.ID), index=p.index), lineno)

        # ID only -> Var location
        if hasattr(p, "ID") and not hasattr(p, "index"):
            return _L(Var(p.ID), lineno)

        # literals
        if hasattr(p, "INT_LITERAL"):
            try:
                val = int(p.INT_LITERAL)
            except Exception:
                val = int(p.INT_LITERAL, 10)
            return _L(Integer(value=val), lineno)
        if hasattr(p, "FLOAT_LITERAL"):
            return _L(Float(value=float(p.FLOAT_LITERAL)), lineno)
        if hasattr(p, "CHAR_LITERAL"):
            s = p.CHAR_LITERAL
            # quitar comillas simples si están presentes
            if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
                s = s[1:-1]
            return _L(Char(value=s), lineno)
        if hasattr(p, "STRING_LITERAL"):
            s = p.STRING_LITERAL
            # quitar comillas dobles si están presentes
            if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
                s = s[1:-1]
            return _L(String(value=s), lineno)
        if hasattr(p, "TRUE"):
            return _L(Boolean(value=True), lineno)
        if hasattr(p, "FALSE"):
            return _L(Boolean(value=False), lineno)

        return None

    # index: '[' assignment ']'  (para ArrayAccess)
    @_("'[' assignment ']'")
    def index(self, p):
        return p.assignment

    # ------------------------------
    # LValues (para la izquierda de asignaciones)
    # ------------------------------
    @_('ID')
    def lval(self, p):
        lineno = first_lineno(p)
        return _L(VarLoc(p.ID), lineno)

    @_('ID "[" assignment "]"')
    def lval(self, p):
        lineno = first_lineno(p)
        return _L(ArrayLoc(name=p.ID, index=p.assignment), lineno)

    # ------------------------------
    # Stubs para if/for (no pedidas aún)
    # ------------------------------
    @_("empty")
    def if_stmt_closed(self, p):
        return None

    @_("empty")
    def if_stmt_open(self, p):
        return None

    @_("empty")
    def for_stmt_closed(self, p):
        return None

    @_("empty")
    def for_stmt_open(self, p):
        return None

    @_("empty")
    def opt_expr(self, p):
        return None

    @_("empty")
    def opt_expr_list(self, p):
        return []


    # ------------------------------
    # Helpers
    # ------------------------------
    @_("")
    def empty(self, p):
        return None

    def error(self, p):
        lineno = p.lineno if p else "EOF"
        value = repr(p.value) if p else "EOF"
        error(f"Syntax error at {value}", lineno)


# ------------------------------
# AST -> dict helper (puede usarse por tests)
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


# Helper para depurar tokens
def debug_tokens(source):
    l = Lexer()
    for t in l.tokenize(source):
        print(t)


if __name__ == "__main__":
    # prueba rápida
    src = "do { x = x + 1; } while (x < 10);"
    debug_tokens(src)
    ast = parse(src)
    print(ast_to_dict(ast))
