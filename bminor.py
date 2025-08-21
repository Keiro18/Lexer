# bminor.py
#
# Punto de entrada para ejecutar el analizador léxico de B-Minor 2025
# Uso:
#   python bminor.py --scan archivo.bminor
#   python bminor.py --test   (ejecuta todos los archivos en test/scanner)

import sys
import os
import subprocess
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

def run_tests():
    TEST_DIR = "test/scanner"
    files = sorted(os.listdir(TEST_DIR))
    total = len(files)
    passed = 0

    for fname in files:
        path = os.path.join(TEST_DIR, fname)
        print(f"\n🔎 Probando {fname}...")
        result = subprocess.run(
            [sys.executable, "bminor.py", "--scan", path],
            capture_output=True,
            text=True
        )
        output = result.stdout + result.stderr
        exitcode = result.returncode

        if fname.startswith("good"):
            if exitcode == 0:
                print("✅ OK")
                passed += 1
            else:
                print("❌ ERROR (falló, debería ser válido)")
                print(output)

        elif fname.startswith("bad"):
            if exitcode != 0:
                print("✅ OK (error detectado)")
                passed += 1
                print(output.strip())
            else:
                print("❌ ERROR (pasó como válido, debería fallar)")
                print(output)

    print(f"\nResumen: {passed}/{total} pruebas correctas")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python bminor.py --scan archivo.bminor | --test")
        sys.exit(1)

    if sys.argv[1] == "--scan":
        if len(sys.argv) != 3:
            print("Uso: python bminor.py --scan archivo.bminor")
            sys.exit(1)
        filename = sys.argv[2]
        status = scan_file(filename)
        sys.exit(status)

    elif sys.argv[1] == "--test":
        run_tests()
        sys.exit(0)

    else:
        print("Opción no válida. Usa --scan o --test")
        sys.exit(1)
