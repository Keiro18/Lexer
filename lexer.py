# lexer.py
#
# Analizador Léxico para el lenguaje B-Minor

import sly

class Lexer(sly.Lexer):
    # Lista de tokens
    tokens = {
        # Palabras reservadas
        ARRAY, AUTO, BOOLEAN, CHAR, ELSE, FALSE, FLOAT, FOR, FUNCTION,
        IF, INTEGER, PRINT, RETURN, STRING, TRUE, VOID, WHILE,
        SWITCH, DO,

        # Literales
        INT_LITERAL, FLOAT_LITERAL, CHAR_LITERAL, STRING_LITERAL,

        # Identificadores
        ID,

        # Operadores lógicos y comparación
        LOR, LAND, EQ, NE, LE, LT, GE, GT, INC, DEC, NOT
    }


    # Símbolos de un solo carácter
    literals = '+-*/%^=()[]{}:;,'

    # Ignorar espacios y tabulaciones
    ignore = ' \t\r'

    # Ignorar comentarios C++
    @_(r'//.*')
    def ignore_cppcomment(self, t):
        pass

    # Ignorar comentarios estilo C
    # Comentarios estilo C bien formados
    @_(r'/\*(.|\n)*?\*/')
    def ignore_comment(self, t):
        self.lineno += t.value.count('\n')

    # Comentarios estilo C sin cierre (error)
    @_(r'/\*([^*]|\*(?!/))*$')
    def error_unclosed_comment(self, t):
        print(f"Line {self.lineno}: Unclosed comment")
        self.index = len(self.text)   # Forzar fin del análisis


    # Contar saltos de línea
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    # Palabras reservadas y IDs
    ID = r'[_a-zA-Z]\w*'
    ID['array']    = ARRAY
    ID['auto']     = AUTO
    ID['boolean']  = BOOLEAN
    ID['char']     = CHAR
    ID['else']     = ELSE
    ID['false']    = FALSE
    ID['float']    = FLOAT
    ID['for']      = FOR
    ID['function'] = FUNCTION
    ID['if']       = IF
    ID['integer']  = INTEGER
    ID['print']    = PRINT
    ID['return']   = RETURN
    ID['string']   = STRING
    ID['true']     = TRUE
    ID['void']     = VOID
    ID['while']    = WHILE
    ID['switch']   = SWITCH
    ID['do']       = DO


    # Operadores múltiples
    LOR = r'\|\|'
    LAND = r'&&'
    EQ = r'=='
    NE = r'!='
    LE = r'<='
    GE = r'>='
    LT = r'<'
    GT = r'>'
    INC = r'\+\+'
    DEC = r'--'
    NOT = r'!'

    # Literales numéricos
    FLOAT_LITERAL = r'([0-9]+\.[0-9]+|\.[0-9]+)([eE][+-]?[0-9]+)?|[0-9]+[eE][+-]?[0-9]+'

    INT_LITERAL = r'[+-]?\d+(?![A-Za-z_])'

    # Literal de carácter (incluyendo escapes válidos)
    CHAR_LITERAL = r"'(\\[abefnrtv\\\'\"]|\\0x[0-9A-Fa-f]{2}|[ -~])'"

    # Literal de cadena
    STRING_LITERAL = r'"(\\[abefnrtv\\\'\"]|\\0x[0-9A-Fa-f]{2}|[ -~])*"'

    def error(self, t):
        print(f"Line {self.lineno}: Bad character '{t.value[0]}'")
        self.index += 1

    # Caso especial: número seguido de '.' sin dígitos después = error
    @_(r'[0-9]+\.(?![0-9])')
    def invalid_float(self, t):
        print(f"Line {self.lineno}: Invalid float literal '{t.value}'")
        self.index += len(t.value)



def tokenize(txt):
    lexer = Lexer()
    for tok in lexer.tokenize(txt):
        print(tok)


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("usage: python lexer.py filename")
        exit(1)
    with open(sys.argv[1], encoding='utf-8') as f:
        tokenize(f.read())
