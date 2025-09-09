# grammar.py
import logging
import sly
from rich import print

from lexer  import Lexer
from errors import error, errors_detected
from model  import *    # AST Definitions


def _L(node, lineno):
    node.lineno = lineno
    return node


class Parser(sly.Parser):
    log = logging.getLogger()
    log.setLevel(logging.ERROR)
    expected_shift_reduce = 1
    debugfile='grammar.txt'

    tokens = Lexer.tokens

    @_("decl_list")
    def prog(self, p):
        return _L(Program(p.decl_list), p.lineno)
    
    # ---------------- DECLARATIONS ----------------

    @_('decl decl_list')
    def decl_list(self, p):
        return [ p.decl ] + p.decl_list

    @_('empty')
    def decl_list(self, p):
        return []

    @_('ID ":" type_simple ";"')
    def decl(self, p):
        return _L(Decl(p.ID, p.type_simple, None), p.lineno)

    @_('ID ":" type_array_sized ";"')
    def decl(self, p):
        return _L(Decl(p.ID, p.type_array_sized, None), p.lineno)

    @_('ID ":" type_func ";"')
    def decl(self, p):
        return _L(Decl(p.ID, p.type_func, None), p.lineno)

    @_('decl_init')
    def decl(self, p):
        return p.decl_init

    @_('ID ":" type_simple "=" expr ";"')
    def decl_init(self, p):
        return _L(Decl(p.ID, p.type_simple, p.expr), p.lineno)

    @_('ID ":" type_array_sized "=" "{" opt_expr_list "}" ";"')
    def decl_init(self, p):
        return _L(Decl(p.ID, p.type_array_sized, p.opt_expr_list), p.lineno)

    @_('ID ":" type_func "=" "{" opt_stmt_list "}"')
    def decl_init(self, p):
        return _L(FuncDecl(p.ID, p.type_func, p.opt_stmt_list), p.lineno)
    
    # ---------------- STATEMENTS ----------------

    @_('stmt_list')
    def opt_stmt_list(self, p):
        return p.stmt_list

    @_('empty')
    def opt_stmt_list(self, p):
        return []

    @_('stmt stmt_list')
    def stmt_list(self, p):
        return [p.stmt] + p.stmt_list

    @_('stmt')
    def stmt_list(self, p):
        return [p.stmt]

    @_('open_stmt')
    @_('closed_stmt')
    def stmt(self, p):
        return p[0]

    @_('if_stmt_closed')
    @_('for_stmt_closed')
    @_('simple_stmt')
    def closed_stmt(self, p):
        return p[0]
        
    @_('if_stmt_open', 'for_stmt_open')
    def open_stmt(self, p):
        return p[0]
        
    @_('IF "(" opt_expr ")"')
    def if_cond(self, p):
        return p.opt_expr

    @_('if_cond closed_stmt ELSE closed_stmt')
    def if_stmt_closed(self, p):
        return _L(IfStmt(p.if_cond, p.closed_stmt0, p.closed_stmt1), p.lineno)
    
    @_('if_cond stmt')    
    def if_stmt_open(self, p):
        return _L(IfStmt(p.if_cond, p.stmt, None), p.lineno)
        
    @_('if_cond closed_stmt ELSE if_stmt_open')    
    def if_stmt_open(self, p):
        return _L(IfStmt(p.if_cond, p.closed_stmt, p.if_stmt_open), p.lineno)

    @_('FOR "(" opt_expr ";" opt_expr ";" opt_expr ")"')
    def for_header(self, p):
        return (p.opt_expr0, p.opt_expr1, p.opt_expr2)

    @_('for_header open_stmt')
    def for_stmt_open(self, p):
        return _L(ForStmt(*p.for_header, p.open_stmt), p.lineno)
        
    @_('for_header closed_stmt')
    def for_stmt_closed(self, p):
        return _L(ForStmt(*p.for_header, p.closed_stmt), p.lineno)
        
    # Simple statements

    @_('print_stmt')
    @_('return_stmt')
    @_('block_stmt')
    @_('decl')
    @_('expr ";"')
    def simple_stmt(self, p):
        return p[0]

    @_('PRINT opt_expr_list ";"')
    def print_stmt(self, p):
        return _L(PrintStmt(p.opt_expr_list), p.lineno)
        
    @_('RETURN opt_expr ";"')
    def return_stmt(self, p):
        return _L(ReturnStmt(p.opt_expr), p.lineno)

    @_('"{" stmt_list "}"')
    def block_stmt(self, p):
        return BlockStmt(p.stmt_list)
    
    # ---------------- EXPRESSIONS ----------------

    @_('empty')
    def opt_expr_list(self, p):
        return []

    @_('expr_list')
    def opt_expr_list(self, p):
        return p.expr_list
        
    @_('expr "," expr_list')
    def expr_list(self, p):
        return [p.expr] + p.expr_list
        
    @_('expr')
    def expr_list(self, p):
        return [p.expr]

    @_('empty')
    def opt_expr(self, p):
        return None

    @_('expr')
    def opt_expr(self, p):
        return p.expr

    @_('expr1')
    def expr(self, p):
        return p.expr1

    @_('lval "=" expr1')
    def expr1(self, p):
        return Assign(p.lval, p.expr1)
        
    @_('expr2')
    def expr1(self, p):
        return p.expr2

    @_('ID')
    def lval(self, p):
        return Var(p.ID)

    @_('ID index')
    def lval(self, p):
        return ArrayAccess(Var(p.ID), p.index)

    @_('expr2 LOR expr3')
    def expr2(self, p):
        return BinOper(p[1], p.expr2, p.expr3)

    @_('expr3')
    def expr2(self, p):
        return p.expr3

    @_('expr3 LAND expr4')
    def expr3(self, p):
        return BinOper(p[1], p.expr3, p.expr4)

    @_('expr4')
    def expr3(self, p):
        return p.expr4

    @_('expr4 EQ expr5')
    @_('expr4 NE expr5')
    @_('expr4 LT expr5')
    @_('expr4 LE expr5')
    @_('expr4 GT expr5')
    @_('expr4 GE expr5')
    def expr4(self, p):
        return BinOper(p[1], p.expr4, p.expr5)

    @_('expr5')
    def expr4(self, p):
        return p.expr5

    @_('expr5 "+" expr6')
    @_('expr5 "-" expr6')
    def expr5(self, p):
        return BinOper(p[1], p.expr5, p.expr6)

    @_('expr6')
    def expr5(self, p):
        return p.expr6

    @_('expr6 "*" expr7')
    @_('expr6 "/" expr7')
    @_('expr6 "%" expr7')
    def expr6(self, p):
        return BinOper(p[1], p.expr6, p.expr7)

    @_('expr7')
    def expr6(self, p):
        return p.expr7

    @_('expr7 "^" expr8')
    def expr7(self, p):
        return BinOper(p[1], p.expr7, p.expr8)

    @_('expr8')
    def expr7(self, p):
        return p.expr8
        
    @_('"-" expr8')
    @_('NOT expr8')
    def expr8(self, p):
        return UnaryOper(p[0], p.expr8)
        
    @_('expr9')
    def expr8(self, p):
        return p.expr9

    @_('expr9 INC')
    def expr9(self, p):
        return UnaryOper('++', p.expr9)
        
    @_('expr9 DEC')
    def expr9(self, p):
        return UnaryOper('--', p.expr9)
        
    @_('group')
    def expr9(self, p):
        return p.group
        
    @_('"(" expr ")"')
    def group(self, p):
        return p.expr
        
    @_('ID "(" opt_expr_list ")"')
    def group(self, p):
        return Call(p.ID, p.opt_expr_list)

    @_('ID index')
    def group(self, p):
        return ArrayAccess(Var(p.ID), p.index)
    
    @_('factor')
    def group(self, p):
        return p.factor
        
    @_('"[" expr "]"')
    def index(self, p):
        return p.expr

    @_('ID')
    def factor(self, p):
        return Var(p.ID)

    @_('INT_LITERAL')
    def factor(self, p):
        return _L(Integer(p.INT_LITERAL), p.lineno)

    @_('FLOAT_LITERAL')
    def factor(self, p):
        return _L(Float(p.FLOAT_LITERAL), p.lineno)

    @_('CHAR_LITERAL')
    def factor(self, p):
        return _L(Char(p.CHAR_LITERAL), p.lineno)
        
    @_('STRING_LITERAL')
    def factor(self, p):
        return _L(String(p.STRING_LITERAL), p.lineno)
        
    @_('TRUE')
    @_('FALSE')
    def factor(self, p):
        return _L(Boolean(p[0] == 'true'), p.lineno)

    # ---------------- TYPES ----------------

    @_('INTEGER')
    @_('FLOAT')
    @_('BOOLEAN')
    @_('CHAR')
    @_('STRING')
    @_('VOID')
    def type_simple(self, p):
        return p[0]
    
    @_('ARRAY "[" "]" type_simple')
    @_('ARRAY "[" "]" type_array')
    def type_array(self, p):
        return ArrayType(None, p[-1])

    @_('ARRAY index type_simple')
    @_('ARRAY index type_array_sized')
    def type_array_sized(self, p):
        return ArrayType(p.index, p[-1])

    @_('FUNCTION type_simple "(" opt_param_list ")"')
    @_('FUNCTION type_array_sized "(" opt_param_list ")"')
    def type_func(self, p):
        return FuncType(p[1], p.opt_param_list)

    @_('empty')
    def opt_param_list(self, p):
        return []

    @_('param_list')
    def opt_param_list(self, p):
        return p.param_list

    @_('param_list "," param')
    def param_list(self, p):
        return p.param_list + [p.param]

    @_('param')
    def param_list(self, p):
        return [p.param]
    
    @_('ID ":" type_simple')
    def param(self, p):
        return Param(p.ID, p.type_simple)

    @_('ID ":" type_array')
    def param(self, p):
        return Param(p.ID, p.type_array)

    @_('ID ":" type_array_sized')
    def param(self, p):
        return Param(p.ID, p.type_array_sized)

    @_('')
    def empty(self, p):
        return None

    def error(self, p):
        lineno = p.lineno if p else 'EOF'
        value = repr(p.value) if p else 'EOF'
        error(f'Syntax error at {value}', lineno)



# ---------------- AST helper ----------------
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

if __name__ == '__main__':
    import sys, json
    
    if sys.platform != 'ios':
        if len(sys.argv) != 2:
            raise SystemExit("Usage: python gparse.py <filename>")
        filename = sys.argv[1]
    else:
        from File_Picker import file_picker_dialog
        filename = file_picker_dialog(
            title='Seleccionar una archivo',
            root_dir='./test',
            file_pattern='^.*[.]bminor'
        )

    if filename:
        txt = open(filename, encoding='utf-8').read()
        ast = parse(txt)
        print(json.dumps(ast_to_dict(ast), indent=2))
