# bminor_lexer.py
# Analizador léxico para el lenguaje B-Minor 
# Compatible con SLY
import sly
import sys
from errors import lexer_error  # Archivo de manejo de errores externo

class BMinorLexer(sly.Lexer):
    # -------------------
    # Lista de tokens (como strings)
    # -------------------
    tokens = {
        # Palabras reservadas
        'ARRAY', 'AUTO', 'BOOLEAN', 'CHAR', 'ELSE', 'FALSE', 'FLOAT', 'FOR', 'FUNCTION',
        'IF', 'INTEGER', 'RETURN', 'STRING', 'TRUE', 'VOID', 'WHILE', 'DO', 'PRINT',
        
        # Literales
        'FLOAT_LIT', 'CHAR_LIT', 'STRING_LIT', 'INT_LIT',
        
        # Operadores multi-caracter
        'LE', 'GE', 'EQ', 'NE', 'LAND', 'LOR', 'INC', 'DEC',
        
        # Operadores unarios
        'NOT',
        
        # Identificadores
        'ID'
    }

    # -------------------
    # Literales de un solo carácter (quitamos '!' porque usamos NOT token)
    # -------------------
    literals = '+-*/%^=()[]{}:;,<>'

    # -------------------
    # Ignorar espacios, tabs y retorno de carro
    # -------------------
    ignore = ' \t\r'

    # -------------------
    # Manejo de líneas nuevas
    # -------------------
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    # -------------------
    # Comentarios estilo C y C++
    # -------------------
    @_(r'//.*')
    def ignore_cpp_comment(self, t):
        pass

    @_(r'/\*(.|\n)*?\*/')
    def ignore_c_comment(self, t):
        self.lineno += t.value.count('\n')

    # -------------------
    # Diccionario de palabras reservadas
    # -------------------
    keywords = {
        'array': 'ARRAY',
        'auto': 'AUTO',
        'boolean': 'BOOLEAN',
        'char': 'CHAR',
        'else': 'ELSE',
        'false': 'FALSE',
        'float': 'FLOAT',
        'for': 'FOR',
        'function': 'FUNCTION',
        'if': 'IF',
        'integer': 'INTEGER',
        'print': 'PRINT',
        'return': 'RETURN',
        'string': 'STRING',
        'true': 'TRUE',
        'void': 'VOID',
        'while': 'WHILE',
        'do': 'DO'
    }

    # -------------------
    # Identificadores y palabras clave
    # -------------------
    @_(r'[a-zA-Z_][a-zA-Z0-9_]*')
    def ID(self, t):
        t.type = self.keywords.get(t.value.lower(), 'ID')
        return t

    # -------------------
    # Operadores multi-caracter
    # -------------------
    LE   = r'<='
    GE   = r'>='
    EQ   = r'=='
    NE   = r'!='
    LAND = r'&&'
    LOR  = r'\|\|'
    INC  = r'\+\+'
    DEC  = r'--'
    NOT  = r'!'

    # -------------------
    # Números flotantes 
    # -------------------
    @_(r'\d+\.\d+([eE][+-]?\d+)?|\d+[eE][+-]?\d+')
    def FLOAT_LIT(self, t):
        try:
            t.value = float(t.value)
        except ValueError:
            lexer_error(self.lineno, t.value)
            return None
        return t

    # -------------------
    # Números enteros
    # -------------------
    @_(r'(0|[1-9][0-9]*)')
    def INT_LIT(self, t):
        t.value = int(t.value)
        return t

    # -------------------
    # Literales de carácter
    # -------------------
    @_(r"'(\\[abefnrtv\\\'\"0x][0-9a-fA-F]*|[^\\'])'")
    def CHAR_LIT(self, t):
        s = t.value[1:-1]
        try:
            t.value = bytes(s, "utf-8").decode("unicode_escape")
        except Exception:
            lexer_error(self.lineno, t.value)
            return None
        return t

    # -------------------
    # Literales de cadena
    # -------------------
    @_(r'"(\\[abefnrtv\\\'\"0x][0-9a-fA-F]*|[^\\"])*"')
    def STRING_LIT(self, t):
        s = t.value[1:-1]
        if len(s) > 255:
            lexer_error(self.lineno, t.value)
            return None
        try:
            t.value = bytes(s, "utf-8").decode("unicode_escape")
        except Exception:
            lexer_error(self.lineno, t.value)
            return None
        return t

    # -------------------
    # Manejo de errores
    # -------------------
    def error(self, t):
        lexer_error(self.lineno, t.value)
        self.index += 1


# -------------------
# Ejecución independiente (para pruebas)
# -------------------
def tokenize_file(filename):
    lexer = BMinorLexer()
    with open(filename, encoding="utf-8") as f:
        text = f.read()
    for tok in lexer.tokenize(text):
        print(tok)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python bminor_lexer.py archivo.bminor")
        sys.exit(1)
    tokenize_file(sys.argv[1])
