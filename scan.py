# scan.py
# Ejecuta el analizador léxico (lexer) B-Minor y muestra los tokens
from bminor_lexer import BMinorLexer
import sys

def main():
    if len(sys.argv) != 2:
        print("Uso: python scan.py archivo.bminor")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, encoding="utf-8") as f:
        text = f.read()

    lexer = BMinorLexer()
    for token in lexer.tokenize(text):
        print(token)

if __name__ == "__main__":
    main()
