# bminor.py
#
# Punto de entrada para ejecutar el analizador léxico de B-Minor 2025
# Uso:
#   python bminor.py --scan archivo.bminor
#   python bminor.py --test scanner
#   python bminor.py --test validationAgainstExamples

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

def run_tests(test_dir):
    if not os.path.exists(test_dir):
        print(f"⚠️ Carpeta {test_dir} no encontrada.")
        return

    files = sorted(os.listdir(test_dir))
    total = len(files)
    passed = 0

    for fname in files:
        path = os.path.join(test_dir, fname)
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

        else:
            # En validationAgainstExamples quizás no todos empiecen con good/bad
            # Así que solo imprimimos el resultado
            if exitcode == 0:
                print("✅ OK (tokenizado)")
                passed += 1
            else:
                print("❌ ERROR (falló)")
                print(output)

    print(f"\nResumen: {passed}/{total} pruebas correctas en {test_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python bminor.py --scan archivo.bminor | --test [scanner|validationAgainstExamples]")
        sys.exit(1)

    if sys.argv[1] == "--scan":
        if len(sys.argv) != 3:
            print("Uso: python bminor.py --scan archivo.bminor")
            sys.exit(1)
        filename = sys.argv[2]
        status = scan_file(filename)
        sys.exit(status)

    elif sys.argv[1] == "--test":
        if len(sys.argv) == 2:
            test_dir = "test/scanner"
        else:
            test_dir = f"test/{sys.argv[2]}"
        run_tests(test_dir)
        sys.exit(0)

    else:
        print("Opción no válida. Usa --scan o --test [carpeta]")
        sys.exit(1)
