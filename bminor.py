# bminor.py
#
# Punto de entrada para ejecutar el analizador léxico de B-Minor 2025

import sys
from lexer import Lexer

def scan_file(filename):
    lexer = Lexer()
    try:
        with open(filename, encoding="utf-8") as f:
            data = f.read()
            for tok in lexer.tokenize(data):
                print(tok)
        return 0  # éxito
    except Exception as e:
        print(f"Error: {e}")
        return 1  # error

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "--scan":
        print("Uso: python bminor.py --scan archivo.bminor")
        sys.exit(1)

    filename = sys.argv[2]
    status = scan_file(filename)
    sys.exit(status)
