# 🧩 Documentación del Compilador B-MINOR

**Materia:** Compiladores  
**Lenguaje:** Python 3  
**Estudiantes:** _Andrés Mogollón, Juan Malagón y Felipe M_  
**Universidad:** _Universidad Tecnológica De Pereira_

---

## 📘 Descripción general

El **compilador `bminor`** está desarrollado en Python utilizando la librería **SLY (Sly Lexer y Parser)**.  
Actualmente implementa las siguientes fases del proceso de compilación:

1. ✅ **Análisis léxico (scanner/tokenizer)**
2. ✅ **Análisis sintáctico (parser)**
3. ✅ **Generación del Árbol de Sintaxis Abstracta (AST)**
4. ✅ **Análisis semántico (checker)**
5. ✅ **Intérprete AST-Walking**
6. ✅ **Generación de archivos de salida para visualización del AST**
   - Archivo `.dot` (Graphviz)
   - Archivo `.pdf` (AST gráfico)

---

## ⚙️ Estructura del proyecto

```
COMPILADOR_BMINOR/
│
├── bminor.py              # Programa principal (análisis léxico y sintáctico)
├── bminor_lexer.py        # Analizador léxico (definición de tokens)
├── bminor_parser.py       # Analizador sintáctico (definición de gramática)
├── bminor_ast.py          # Definición de nodos del árbol sintáctico
├── astprint.py            # Generador y visualizador del AST
│
├── checker.py             # ✨ Analizador semántico (verificación de tipos)
├── interp.py              # ✨ Intérprete AST-Walking
├── bminor_builtins.py     # ✨ Funciones built-in (print, len, int, etc.)
├── symtab.py              # Tabla de símbolos
├── typesys.py             # Sistema de tipos
├── errors.py              # Manejo de errores
├── model.py               # Modelos alternativos de AST
│
├── dot/                   # 📂 Carpeta de salida para los gráficos DOT y PDF
│   ├── sieve.dot
│   └── sieve.pdf
│
└── test/                  # 📂 Carpeta con archivos fuente de prueba
    ├── scanner/
    ├── validationAgainstExamples/
    ├── test_complete_fixed.bminor    # ✨ Suite completa de pruebas
    ├── test_basic.bminor             # ✨ Prueba básica
    ├── test_loops.bminor             # ✨ Prueba de ciclos
    ├── test_arrays.bminor            # ✨ Prueba de arrays
    ├── test_recursion.bminor         # ✨ Prueba de recursión
    ├── sieve.bminor
    ├── knight.bminor
    └── mandel.bminor
```

---

## 🧠 Comandos principales

### 🔹 1. **Análisis léxico (scanner)**
Escanea el código fuente y muestra los tokens reconocidos.

```bash
python bminor.py --scan test/sieve.bminor
```

**Salida esperada:**
```
Token(type='ID', value='N', lineno=11, index=645, end=646)
Token(type=':', value=':', lineno=11, index=646, end=647)
Token(type='INTEGER', value='integer', lineno=11, index=648, end=655)
...
```

Cada token muestra:
- **type:** tipo de token (ID, INT_LIT, FOR, etc.)
- **value:** valor léxico
- **lineno:** número de línea donde aparece
- **index / end:** posición dentro del archivo

---

### 🔹 2. **Análisis sintáctico (parser)**
Analiza la estructura del programa según la gramática definida.

```bash
python bminor.py --parse test/sieve.bminor
```

**Salida esperada:**
```
============================================================
Análisis sintáctico exitoso!
============================================================
```

Si hay errores, se mostrarán con la línea y el token problemático.

---

### 🔹 3. **Generación y visualización del AST**
Construye el Árbol de Sintaxis Abstracta y lo muestra de forma textual y gráfica.

```bash
python astprint.py test/sieve.bminor
```

**Salida esperada (resumen):**
```
✓ Análisis sintáctico exitoso!

═══════════════════════════════════════════════════════
           AST - Árbol de Sintaxis Abstracta
═══════════════════════════════════════════════════════

└── Program
    ├── VarDeclInit N: integer
    │   └── init:
    │       └── 100 (int)
    ├── VarDecl isprime: array[] boolean
    └── FuncDecl main() → void
        └── body:
            ├── VarDecl i: integer
            ├── VarDecl j: integer
            ├── For
            │   ├── init:
            │   │   └── = (assign)
            │   │       ├── left: i (id)
            │   │       └── right: 0 (int)
            │   ├── condition: <= (binop)
            │   └── body: ...
```

**Archivos generados:**
- `dot/sieve.dot` - Código Graphviz
- `dot/sieve.pdf` - Gráfico del AST en PDF

👉 Visualizar `.dot` en línea: [GraphvizOnline](https://dreampuf.github.io/GraphvizOnline/)

---

### 🔹 4. **✨ Análisis semántico (checker)**
Verifica tipos, alcance de variables, declaraciones de funciones y consistencia semántica.

```bash
python checker.py test/test_basic.bminor
```

**Salida esperada:**
```
============================================================
Iniciando análisis semántico...
============================================================

✓ Análisis semántico exitoso!

Tabla de símbolos:
  Scope: global
    a: integer
    b: integer
    suma: function(integer, integer) -> integer
    main: function() -> integer
```

**Si hay errores:**
```
Error semántico: Variable 'x' no definida
Error semántico: Tipos incompatibles en asignación: 'integer' = 'string'
✗ Se encontraron 2 errores semánticos
```

---

### 🔹 5. **✨ Ejecución con intérprete (interp.py)**
Ejecuta el programa B-Minor directamente sin compilar a código máquina.

```bash
python interp.py test/test_basic.bminor
```

**Salida esperada:**
```
Parseando...
✓ Parsing exitoso

Ejecutando análisis semántico...
✓ Análisis semántico exitoso

Ejecutando programa...
============================================================
=== PRUEBA BASICA ===
a = 5
b = 10
c = 3.14
mensaje = Hola B-Minor
flag = True

a + b = 15
b - a = 5
a * b = 50
b / a = 2

suma(a, b) = 15

============================================================
✓ Ejecución completada
```

---

## 🧪 Suite de Pruebas

El compilador incluye una **suite completa de archivos de prueba** para validar todas las características implementadas.

### 📁 Archivos de Prueba Disponibles

| Archivo | Descripción | Características |
|---------|-------------|-----------------|
| `test_complete_fixed.bminor` | **Suite completa** | Variables, arrays, funciones, recursión, ordenamiento, todos los operadores y estructuras de control |
| `test_basic.bminor` | Prueba básica | Variables, operaciones aritméticas, funciones simples |
| `test_loops.bminor` | Prueba de ciclos | while, do-while, for, ciclos anidados |
| `test_arrays.bminor` | Prueba de arrays | Declaración, acceso, modificación, búsqueda, operaciones |
| `test_recursion.bminor` | Prueba de recursión | Factorial, Fibonacci, MCD, suma de dígitos |

### 🚀 Ejecutar las Pruebas

#### Prueba individual:
```bash
# Prueba básica (recomendado empezar aquí)
python interp.py test/test_basic.bminor

# Prueba completa (todas las características)
python interp.py test/test_complete_fixed.bminor

# Pruebas específicas
python interp.py test/test_loops.bminor
python interp.py test/test_arrays.bminor
python interp.py test/test_recursion.bminor
```

#### Ejecutar todas las pruebas (Bash/Linux/Mac):
```bash
for file in test/test_*.bminor; do
    echo "========================================="
    echo "Ejecutando: $file"
    echo "========================================="
    python interp.py "$file"
    echo ""
done
```

#### Ejecutar todas las pruebas (PowerShell/Windows):
```powershell
Get-ChildItem test/test_*.bminor | ForEach-Object {
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "Ejecutando: $($_.Name)" -ForegroundColor Yellow
    Write-Host "=========================================" -ForegroundColor Cyan
    python interp.py $_.FullName
    Write-Host ""
}
```

### ✅ Checklist de Características Probadas

- [x] **Tipos de datos:** integer, float, boolean, char, string, arrays
- [x] **Operadores aritméticos:** +, -, *, /, %, ^ (potencia)
- [x] **Operadores de comparación:** <, <=, >, >=, ==, !=
- [x] **Operadores lógicos:** &&, ||, !
- [x] **Incremento/Decremento:** ++, --
- [x] **Estructuras de control:** if-else, while, do-while, for
- [x] **Funciones:** declaración, llamadas, parámetros, return
- [x] **Recursión:** factorial, fibonacci, algoritmos recursivos
- [x] **Arrays:** declaración, inicialización, acceso, modificación
- [x] **Algoritmos:** ordenamiento (bubble sort), búsqueda
- [x] **Scopes:** variables globales, locales, bloques anidados
- [x] **Funciones built-in:** print, len, int, float, str, exit

---

## 🗂️ Flujo completo de compilación/ejecución

```bash
# 1. Análisis léxico
python bminor.py --scan test/test_basic.bminor

# 2. Análisis sintáctico
python bminor.py --parse test/test_basic.bminor

# 3. Visualización del AST
python astprint.py test/test_basic.bminor

# 4. Análisis semántico
python checker.py test/test_basic.bminor

# 5. Ejecución del programa
python interp.py test/test_basic.bminor
```

---

## 🧩 Estado actual del compilador

| Etapa | Estado | Descripción |
|--------|---------|-------------|
| **Análisis léxico** | ✅ Completo | Reconoce todos los tokens: identificadores, literales, operadores, palabras clave |
| **Análisis sintáctico** | ✅ Completo | Gramática completa con precedencia de operadores |
| **AST** | ✅ Completo | Representación jerárquica del programa |
| **Visualización del AST** | ✅ Completo | Exporta a `.dot` y `.pdf` con Graphviz |
| **Análisis semántico** | ✅ Completo | Verificación de tipos, alcance, declaraciones |
| **Intérprete** | ✅ Completo | Ejecución directa mediante AST-Walking |
| **Funciones built-in** | ✅ Completo | print, len, int, float, str, input, exit |
| **Generación de código intermedio** | ⏳ Pendiente | LLVM IR / Bytecode (próxima fase) |
| **Optimizaciones** | ⏳ Pendiente | Optimización de código |

---

## 🧰 Requisitos del entorno

### Dependencias de Python:
```bash
pip install sly rich multimethod
```

### Herramientas adicionales:
- **Python 3.10+**
- **Graphviz** (para visualización del AST)
  ```bash
  # Linux/Mac
  sudo apt install graphviz
  
  # Windows
  # Descargar desde: https://graphviz.org/download/
  ```

---

## 📊 Características del lenguaje B-Minor

### Tipos de datos:
- `integer` - Números enteros
- `float` - Números de punto flotante
- `boolean` - Valores true/false
- `char` - Caracteres individuales
- `string` - Cadenas de texto
- `array [N] tipo` - Arrays de tamaño fijo

### Estructuras de control:
```bminor
// If-Else
if (x > 10) {
    print "Mayor\n";
} else {
    print "Menor\n";
}

// While
while (i < 10) {
    i++;
}

// Do-While
do {
    i--;
} while (i > 0);

// For
for (i = 0; i < 10; i++) {
    print i;
}
```

### Funciones:
```bminor
// Declaración
suma: function integer (a: integer, b: integer) = {
    return a + b;
}

// Recursión
factorial: function integer (n: integer) = {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}
```

### Arrays:
```bminor
// Declaración e inicialización
numeros: array [5] integer = {1, 2, 3, 4, 5};

// Acceso
x: integer = numeros[0];

// Modificación
numeros[2] = 100;
```

---

## 🐛 Debugging y Errores Comunes

### Error: "Variable 'x' no definida"
**Causa:** La variable no fue declarada antes de usarse.
```bminor
// ❌ Incorrecto
print x;

// ✅ Correcto
x: integer = 10;
print x;
```

### Error: "Función 'func' no definida"
**Causa:** La función debe declararse antes de llamarla.
```bminor
// ❌ Incorrecto
main: function integer () = {
    suma(1, 2);  // suma no existe aún
}
suma: function integer (a: integer, b: integer) = { ... }

// ✅ Correcto
suma: function integer (a: integer, b: integer) = { ... }
main: function integer () = {
    suma(1, 2);
}
```

### Error: "Tipos incompatibles en asignación"
**Causa:** Asignación de tipos diferentes.
```bminor
// ❌ Incorrecto
x: integer = "texto";

// ✅ Correcto
x: integer = 10;
y: string = "texto";
```

### Error de sintaxis en `for`
**Causa:** Declaración de variables dentro del cuerpo del `for`.
```bminor
// ❌ Incorrecto
for (i: integer = 0; i < 10; i++) {
    resultado: integer = i * 2;  // Declaración dentro del for
}

// ✅ Correcto
resultado: integer;
for (i: integer = 0; i < 10; i++) {
    resultado = i * 2;  // Solo asignación
}
```

---

## 📚 Recursos Adicionales

- [Especificación de B-Minor](https://www3.nd.edu/~dthain/courses/cse40243/fall2020/bminor.html)
- [Libro: Crafting Interpreters](https://craftinginterpreters.com/)
- [SLY Documentation](https://sly.readthedocs.io/)
- [Graphviz Online Editor](https://dreampuf.github.io/GraphvizOnline/)

---

## 👥 Contribuciones

**Desarrolladores:**
- Andrés Mogollón
- Juan Malagón
- Felipe M

**Universidad Tecnológica de Pereira**  
**Curso:** Compiladores  
**Año:** 2024-2025

---

## 📝 Notas de la Versión

### v2.0 (Actual)
- ✅ Intérprete AST-Walking funcional
- ✅ Análisis semántico completo
- ✅ Suite de pruebas exhaustiva
- ✅ Funciones built-in
- ✅ Soporte completo para recursión
- ✅ Manejo de scopes y bloques

### v1.0
- ✅ Análisis léxico y sintáctico
- ✅ Generación de AST
- ✅ Visualización con Graphviz

---

## 🎯 Próximos Pasos

- [ ] Generación de código intermedio (LLVM IR)
- [ ] Optimizaciones de código
- [ ] Compilación a código máquina
- [ ] Manejo de errores más detallado
- [ ] Depurador interactivo

---

## 📄 Licencia

Este proyecto es parte del curso de Compiladores de la Universidad Tecnológica de Pereira.  
Uso académico exclusivamente.

---

**¡Disfruta programando en B-Minor! 🚀**