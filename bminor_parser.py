# bminor_parser.py
# Analizador sintáctico para el lenguaje B-Minor
# Basado en la gramática oficial de B-Minor 2025
# Compatible con SLY

from sly import Parser
from bminor_lexer import BMinorLexer
try:
    from bminor_ast import *
except ImportError:
    from model import *
import sys

class BMinorParser(Parser):
    # Obtener los tokens del lexer
    tokens = BMinorLexer.tokens
    
    # Definir precedencia y asociatividad de operadores
    precedence = (
        ('right', '='),
        ('left', LOR),
        ('left', LAND),
        ('left', EQ, NE, '<', LE, '>', GE),
        ('left', '+', '-'),
        ('left', '*', '/', '%'),
        ('right', '^'),
        ('right', UMINUS, NOT),
        ('left', INC, DEC),
        ('left', '[', '('),
    )

    # -------------------
    # Programa principal
    # -------------------
    @_('decl_list')
    def prog(self, p):
        return Program(body=p.decl_list)

    # -------------------
    # Lista de declaraciones
    # -------------------
    @_('empty')
    def decl_list(self, p):
        return []

    @_('decl decl_list')
    def decl_list(self, p):
        return [p.decl] + p.decl_list

    # -------------------
    # Declaraciones
    # -------------------
    @_('ID ":" type_simple ";"')
    def decl(self, p):
        return VarDecl(name=p.ID, type=p.type_simple, value=None)

    @_('ID ":" type_array_sized ";"')
    def decl(self, p):
        return VarDecl(name=p.ID, type=p.type_array_sized, value=None)

    @_('ID ":" type_func ";"')
    def decl(self, p):
        return FuncDecl(name=p.ID, type_func=p.type_func, body=None)

    @_('decl_init')
    def decl(self, p):
        return p.decl_init

    # -------------------
    # Declaraciones con inicialización
    # -------------------
    @_('ID ":" type_simple "=" expr ";"')
    def decl_init(self, p):
        return VarDeclInit(name=p.ID, typ=p.type_simple, init=p.expr)

    @_('ID ":" type_array_sized "=" "{" opt_expr_list "}" ";"')
    def decl_init(self, p):
        return VarDeclInit(name=p.ID, typ=p.type_array_sized, init=p.opt_expr_list)

    @_('ID ":" type_func "=" "{" opt_stmt_list "}"')
    def decl_init(self, p):
        return FuncDecl(name=p.ID, type_func=p.type_func, body=p.opt_stmt_list)

    # -------------------
    # Lista opcional de sentencias
    # -------------------
    @_('empty')
    def opt_stmt_list(self, p):
        return []

    @_('stmt_list')
    def opt_stmt_list(self, p):
        return p.stmt_list

    # -------------------
    # Lista de sentencias
    # -------------------
    @_('stmt')
    def stmt_list(self, p):
        return [p.stmt]

    @_('stmt stmt_list')
    def stmt_list(self, p):
        return [p.stmt] + p.stmt_list

    # -------------------
    # Sentencias
    # -------------------
    @_('open_stmt')
    def stmt(self, p):
        return p.open_stmt

    @_('closed_stmt')
    def stmt(self, p):
        return p.closed_stmt

    # -------------------
    # Sentencias cerradas
    # -------------------
    @_('if_stmt_closed')
    def closed_stmt(self, p):
        return p.if_stmt_closed

    @_('for_stmt_closed')
    def closed_stmt(self, p):
        return p.for_stmt_closed

    @_('simple_stmt')
    def closed_stmt(self, p):
        return p.simple_stmt

    # -------------------
    # Sentencias abiertas
    # -------------------
    @_('if_stmt_open')
    def open_stmt(self, p):
        return p.if_stmt_open

    @_('for_stmt_open')
    def open_stmt(self, p):
        return p.for_stmt_open

    # -------------------
    # Condición IF
    # -------------------
    @_('IF "(" opt_expr ")"')
    def if_cond(self, p):
        return p.opt_expr

    # -------------------
    # Sentencia IF cerrada
    # -------------------
    @_('if_cond closed_stmt ELSE closed_stmt')
    def if_stmt_closed(self, p):
        return IfStmt(cond=p.if_cond, then_branch=p.closed_stmt0, else_branch=p.closed_stmt1)

    # -------------------
    # Sentencia IF abierta
    # -------------------
    @_('if_cond stmt')
    def if_stmt_open(self, p):
        return IfStmt(cond=p.if_cond, then_branch=p.stmt, else_branch=None)

    @_('if_cond closed_stmt ELSE if_stmt_open')
    def if_stmt_open(self, p):
        return IfStmt(cond=p.if_cond, then_branch=p.closed_stmt, else_branch=p.if_stmt_open)

    # -------------------
    # Encabezado FOR
    # -------------------
    @_('FOR "(" opt_expr ";" opt_expr ";" opt_expr ")"')
    def for_header(self, p):
        return (p.opt_expr0, p.opt_expr1, p.opt_expr2)

    # -------------------
    # Sentencia FOR
    # -------------------
    @_('for_header open_stmt')
    def for_stmt_open(self, p):
        return ForStmt(init=p.for_header[0], cond=p.for_header[1], 
                      step=p.for_header[2], body=p.open_stmt)

    @_('for_header closed_stmt')
    def for_stmt_closed(self, p):
        return ForStmt(init=p.for_header[0], cond=p.for_header[1], 
                      step=p.for_header[2], body=p.closed_stmt)

    # -------------------
    # Sentencias simples
    # -------------------
    @_('print_stmt')
    def simple_stmt(self, p):
        return p.print_stmt

    @_('return_stmt')
    def simple_stmt(self, p):
        return p.return_stmt

    @_('block_stmt')
    def simple_stmt(self, p):
        return p.block_stmt

    @_('decl')
    def simple_stmt(self, p):
        return p.decl

    @_('expr ";"')
    def simple_stmt(self, p):
        return p.expr
    
    # -------------------
    # Sentencia WHILE
    # -------------------
    @_('WHILE "(" expr ")" stmt')
    def while_stmt(self, p):
        return WhileStmt(cond=p.expr, body=p.stmt)

    @_('while_stmt')
    def simple_stmt(self, p):
        return p.while_stmt

    # -------------------
    # Sentencia DO-WHILE
    # -------------------
    @_('DO stmt WHILE "(" expr ")" ";"')
    def dowhile_stmt(self, p):
        return DoWhileStmt(body=p.stmt, cond=p.expr)

    @_('dowhile_stmt')
    def simple_stmt(self, p):
        return p.dowhile_stmt


    # -------------------
    # Sentencia PRINT
    # -------------------
    @_('PRINT opt_expr_list ";"')
    def print_stmt(self, p):
        return PrintStmt(expr=p.opt_expr_list)

    # -------------------
    # Sentencia RETURN
    # -------------------
    @_('RETURN opt_expr ";"')
    def return_stmt(self, p):
        return ReturnStmt(expr=p.opt_expr)

    # -------------------
    # Bloque de sentencias
    # -------------------
    @_('"{" stmt_list "}"')
    def block_stmt(self, p):
        return Block(body=p.stmt_list)

    # -------------------
    # Lista opcional de expresiones
    # -------------------
    @_('empty')
    def opt_expr_list(self, p):
        return []

    @_('expr_list')
    def opt_expr_list(self, p):
        return p.expr_list

    # -------------------
    # Lista de expresiones
    # -------------------
    @_('expr')
    def expr_list(self, p):
        return [p.expr]

    @_('expr "," expr_list')
    def expr_list(self, p):
        return [p.expr] + p.expr_list

    # -------------------
    # Expresión opcional
    # -------------------
    @_('empty')
    def opt_expr(self, p):
        return None

    @_('expr')
    def opt_expr(self, p):
        return p.expr

    # -------------------
    # Expresiones (nivel 1 - asignación)
    # -------------------
    @_('expr1')
    def expr(self, p):
        return p.expr1

    @_('lval "=" expr1')
    def expr1(self, p):
        return Assign(left=p.lval, right=p.expr1)

    @_('expr2')
    def expr1(self, p):
        return p.expr2

    # -------------------
    # L-values
    # -------------------
    @_('ID')
    def lval(self, p):
        return Identifier(name=p.ID)

    @_('ID index')
    def lval(self, p):
        return ArrayAccess(array=Identifier(name=p.ID), index=p.index)

    # -------------------
    # Expresión nivel 2 (OR lógico)
    # -------------------
    @_('expr2 LOR expr3')
    def expr2(self, p):
        return BinOper(oper='||', left=p.expr2, right=p.expr3)

    @_('expr3')
    def expr2(self, p):
        return p.expr3

    # -------------------
    # Expresión nivel 3 (AND lógico)
    # -------------------
    @_('expr3 LAND expr4')
    def expr3(self, p):
        return BinOper(oper='&&', left=p.expr3, right=p.expr4)

    @_('expr4')
    def expr3(self, p):
        return p.expr4

    # -------------------
    # Expresión nivel 4 (comparación)
    # -------------------
    @_('expr4 EQ expr5')
    def expr4(self, p):
        return BinOper(oper='==', left=p.expr4, right=p.expr5)

    @_('expr4 NE expr5')
    def expr4(self, p):
        return BinOper(oper='!=', left=p.expr4, right=p.expr5)

    @_('expr4 "<" expr5')
    def expr4(self, p):
        return BinOper(oper='<', left=p.expr4, right=p.expr5)

    @_('expr4 LE expr5')
    def expr4(self, p):
        return BinOper(oper='<=', left=p.expr4, right=p.expr5)

    @_('expr4 ">" expr5')
    def expr4(self, p):
        return BinOper(oper='>', left=p.expr4, right=p.expr5)

    @_('expr4 GE expr5')
    def expr4(self, p):
        return BinOper(oper='>=', left=p.expr4, right=p.expr5)

    @_('expr5')
    def expr4(self, p):
        return p.expr5

    # -------------------
    # Expresión nivel 5 (suma/resta)
    # -------------------
    @_('expr5 "+" expr6')
    def expr5(self, p):
        return BinOper(oper='+', left=p.expr5, right=p.expr6)

    @_('expr5 "-" expr6')
    def expr5(self, p):
        return BinOper(oper='-', left=p.expr5, right=p.expr6)

    @_('expr6')
    def expr5(self, p):
        return p.expr6

    # -------------------
    # Expresión nivel 6 (multiplicación/división)
    # -------------------
    @_('expr6 "*" expr7')
    def expr6(self, p):
        return BinOper(oper='*', left=p.expr6, right=p.expr7)

    @_('expr6 "/" expr7')
    def expr6(self, p):
        return BinOper(oper='/', left=p.expr6, right=p.expr7)

    @_('expr6 "%" expr7')
    def expr6(self, p):
        return BinOper(oper='%', left=p.expr6, right=p.expr7)

    @_('expr7')
    def expr6(self, p):
        return p.expr7

    # -------------------
    # Expresión nivel 7 (potencia)
    # -------------------
    @_('expr7 "^" expr8')
    def expr7(self, p):
        return BinOper(oper='^', left=p.expr7, right=p.expr8)

    @_('expr8')
    def expr7(self, p):
        return p.expr8

    # -------------------
    # Expresión nivel 8 (unarios)
    # -------------------
    @_('"-" expr8 %prec UMINUS')
    def expr8(self, p):
        return UnaryOper(oper='-', expr=p.expr8)

    @_('NOT expr8')
    def expr8(self, p):
        return UnaryOper(oper='!', expr=p.expr8)

    @_('expr9')
    def expr8(self, p):
        return p.expr9

    # -------------------
    # Expresión nivel 9 (incremento/decremento postfijo)
    # -------------------
    @_('expr9 INC')
    def expr9(self, p):
        return BinOper(oper='++', left=p.expr9, right=None)

    @_('expr9 DEC')
    def expr9(self, p):
        return BinOper(oper='--', left=p.expr9, right=None)

    @_('group')
    def expr9(self, p):
        return p.group

    # -------------------
    # Group (expresiones agrupadas y primarias)
    # -------------------
    @_('"(" expr ")"')
    def group(self, p):
        return p.expr

    @_('ID "(" opt_expr_list ")"')
    def group(self, p):
        return Call(func=Identifier(name=p.ID), args=p.opt_expr_list)

    @_('ID index')
    def group(self, p):
        return ArrayAccess(array=Identifier(name=p.ID), index=p.index)

    @_('factor')
    def group(self, p):
        return p.factor

    # -------------------
    # Índice de array
    # -------------------
    @_('"[" expr "]"')
    def index(self, p):
        return p.expr

    # -------------------
    # Factores (literales e identificadores)
    # -------------------
    @_('ID')
    def factor(self, p):
        return Identifier(name=p.ID)

    @_('FLOAT_LIT')
    def factor(self, p):
        return Float(value=p.FLOAT_LIT)

    @_('INT_LIT')
    def factor(self, p):
        return Integer(value=p.INT_LIT)

    @_('CHAR_LIT')
    def factor(self, p):
        return Char(value=p.CHAR_LIT)

    @_('STRING_LIT')
    def factor(self, p):
        return String(value=p.STRING_LIT)

    @_('TRUE')
    def factor(self, p):
        return Boolean(value=True)

    @_('FALSE')
    def factor(self, p):
        return Boolean(value=False)

    # -------------------
    # Tipos simples
    # -------------------
    @_('INTEGER')
    def type_simple(self, p):
        return SimpleType(name='integer')

    @_('FLOAT')
    def type_simple(self, p):
        return SimpleType(name='float')

    @_('BOOLEAN')
    def type_simple(self, p):
        return SimpleType(name='boolean')

    @_('CHAR')
    def type_simple(self, p):
        return SimpleType(name='char')

    @_('STRING')
    def type_simple(self, p):
        return SimpleType(name='string')

    @_('VOID')
    def type_simple(self, p):
        return SimpleType(name='void')

    # -------------------
    # Tipos array sin tamaño
    # -------------------
    @_('ARRAY "[" "]" type_simple')
    def type_array(self, p):
        return ArrayType(size=None, elem_type=p.type_simple)

    @_('ARRAY "[" "]" type_array')
    def type_array(self, p):
        return ArrayType(size=None, elem_type=p.type_array)

    # -------------------
    # Tipos array con tamaño
    # -------------------
    @_('ARRAY index type_simple')
    def type_array_sized(self, p):
        return ArrayType(size=p.index, elem_type=p.type_simple)

    @_('ARRAY index type_array_sized')
    def type_array_sized(self, p):
        return ArrayType(size=p.index, elem_type=p.type_array_sized)

    # -------------------
    # Tipos función
    # -------------------
    @_('FUNCTION type_simple "(" opt_param_list ")"')
    def type_func(self, p):
        return FuncType(ret_type=p.type_simple, params=p.opt_param_list)

    @_('FUNCTION type_array_sized "(" opt_param_list ")"')
    def type_func(self, p):
        return FuncType(ret_type=p.type_array_sized, params=p.opt_param_list)

    # -------------------
    # Lista opcional de parámetros
    # -------------------
    @_('empty')
    def opt_param_list(self, p):
        return []

    @_('param_list')
    def opt_param_list(self, p):
        return p.param_list

    # -------------------
    # Lista de parámetros
    # -------------------
    @_('param')
    def param_list(self, p):
        return [p.param]

    @_('param_list "," param')
    def param_list(self, p):
        return p.param_list + [p.param]

    # -------------------
    # Parámetros
    # -------------------
    @_('ID ":" type_simple')
    def param(self, p):
        return Param(name=p.ID, typ=p.type_simple)

    @_('ID ":" type_array')
    def param(self, p):
        return Param(name=p.ID, typ=p.type_array)

    @_('ID ":" type_array_sized')
    def param(self, p):
        return Param(name=p.ID, typ=p.type_array_sized)

    # -------------------
    # Producción vacía
    # -------------------
    @_('')
    def empty(self, p):
        pass

    # -------------------
    # Manejo de errores
    # -------------------
    def error(self, p):
        if p:
            print(f"Error de sintaxis en línea {p.lineno}: token inesperado '{p.value}' (tipo: {p.type})")
        else:
            print("Error de sintaxis: fin de archivo inesperado")


# -------------------
# Función principal para pruebas
# -------------------
def parse_file(filename):
    lexer = BMinorLexer()
    parser = BMinorParser()
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
        
        result = parser.parse(lexer.tokenize(text))
        
        if result:
            print("=" * 60)
            print("Análisis sintáctico exitoso!")
            print("=" * 60)
            return result
        else:
            print("Error: No se pudo construir el AST")
            return None
            
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo '{filename}'")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return None


# Función para parsear desde string (útil para astprint.py)
def parse(text):
    lexer = BMinorLexer()
    parser = BMinorParser()
    return parser.parse(lexer.tokenize(text))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python bminor_parser.py archivo.bminor")
        sys.exit(1)
    
    ast = parse_file(sys.argv[1])
    if ast:
        print("\nPara visualizar el AST gráficamente, ejecuta:")
        print(f"  python astprint.py {sys.argv[1]}") 