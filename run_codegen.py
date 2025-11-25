from bminor_lexer import BMinorLexer
from bminor_parser import BMinorParser
from checker import Check
from codegen.codegen import IRGenerator

import sys

if len(sys.argv) != 2:
    print("Uso: python3 run_codegen.py archivo.bminor")
    exit(1)

source_file = sys.argv[1]

with open(source_file, "r") as f:
    source = f.read()

# 1. Lexer + Parser
lexer = BMinorLexer()
parser = BMinorParser()

ast = parser.parse(lexer.tokenize(source))

# 2. Semantic checker
symtab, check_errors = Check.check(ast)

if check_errors:
    print("Errores semánticos encontrados:")
    for err in check_errors:
        print(" -", err)
    exit(1)

# 3. IR Generator
gen = IRGenerator()
module = gen.generate(ast)

print(module)
