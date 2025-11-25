#!/bin/bash

# Verifica argumento
if [ -z "$1" ]; then
    echo "Uso: ./compile.sh archivo.bminor"
    exit 1
fi

SRC="$1"
BASENAME="${SRC%.*}"

echo "Compilando $SRC ..."

python3 run_codegen.py "$SRC" > "$BASENAME.ll" &&
llvm-as "$BASENAME.ll" -o "$BASENAME.bc" &&
llc "$BASENAME.bc" -o "$BASENAME.s" &&
clang "$BASENAME.s" runtime.c -o "$BASENAME" &&
echo "Ejecutable generado: ./$BASENAME"
