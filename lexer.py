import sly

class Lexer(sly.Lexer):
    tokens = {
        ARRAY, AUTO, BOOLEAN, CHAR, ELSE, FALSE, FLOAT, FOR, FUNCTION,
        IF, INTEGER, PRINT, RETURN, STRING, TRUE, VOID, WHILE,
        ID, NUMBER,
        EQEQ, NOTEQ, LE, GE
    }

    literals = '+-*/%^=()[]{}:;,<>!'

    ignore = ' \t\r'

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    @_(r'//.*')
    def ignore_cppcomment(self, t):
        pass

    @_(r'/\*(.|\n)*?\*/')
    def ignore_comment(self, t):
        self.lineno += t.value.count('\n')

    # Palabras reservadas e identificadores
    ID = r'[_a-zA-Z]\w*'
    ID['array'] = ARRAY
    ID['auto']  = AUTO
    ID['boolean'] = BOOLEAN
    ID['char']  = CHAR
    ID['integer'] = INTEGER
    ID['true'] = TRUE
    ID['false'] = FALSE
    ID['function'] = FUNCTION
    ID['for'] = FOR
    ID['if'] = IF
    ID['print'] = PRINT
    ID['return'] = RETURN
    ID['void'] = VOID
    ID['while'] = WHILE
    ID['float'] = FLOAT
    ID['string'] = STRING
    ID['else'] = ELSE

    # Números
    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    # Operadores dobles
    EQEQ = r'=='
    NOTEQ = r'!='
    LE = r'<='
    GE = r'>='

    def error(self, t):
        print(f"Line {self.lineno}: Bad character '{t.value[0]}'")
        self.index += 1

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
