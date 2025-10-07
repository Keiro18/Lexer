# 🧩 Documentación del Compilador BMINOR


**Materia:** Compiladores  
**Lenguaje:** Python 3  
**Estudiantes:** _Andrés Mogollón, Juan Malagón y Felipe M_  
**Universidad:** _Universidad Técnologica De Pereira_

## 📘 Descripción general
El **compilador `bminor`** está siendo desarrollado en Python utilizando la librería **SLY (Sly Lexer y Parser)**.  
Actualmente implementa las siguientes fases del proceso de compilación:

1. **Análisis léxico (scanner/tokenizer)**
2. **Análisis sintáctico (parser)**
3. **Generación del Árbol de Sintaxis Abstracta (AST)**
4. **Generación de archivos de salida para visualización del AST**
   - Archivo `.dot` (Graphviz)
   - Archivo `.pdf` (AST gráfico)

---

## ⚙️ Estructura del proyecto

```
COMPILADOR_2.0/
│
├── bminor.py              # Programa principal (entrada del compilador)
├── lexer.py               # Analizador léxico (definición de tokens)
├── parser.py              # Analizador sintáctico (definición de gramática)
├── astprint.py            # Generador y visualizador del AST
├── ast_nodes.py           # Definición de nodos del árbol sintáctico
│
├── dot/                   # 📂 Carpeta de salida para los gráficos DOT y PDF
│   ├── sieve.dot
│   ├── sieve.pdf
│
└── test/                  # Carpeta con archivos fuente del lenguaje bminor
    ├── scanner/
    ├── validationAgaintsExamples/
    ├── sieve.bminor
    ├── knight.bminor
    ├── mandel.bminor
    ├── bminor_test_file.bminor
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
WARNING: Token(s) {DO, WHILE, AUTO} defined, but not used
WARNING: There are 3 unused tokens
```

Esto indica que los tokens están definidos en el lexer pero aún no utilizados por la gramática.  
Si no hay errores, significa que la estructura sintáctica del programa es válida.

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

---

### 🗂️ Archivos generados automáticamente

Al ejecutar `astprint.py`, se generan los siguientes archivos:

| Tipo | Ruta | Descripción |
|------|------|--------------|
| `.dot` | `dot\sieve.dot` | Código Graphviz para visualizar el AST |
| `.pdf` | `dot\sieve.pdf` | Gráfico del AST exportado en formato PDF |

Puedes visualizar el `.dot` en línea usando:  
👉 [https://dreampuf.github.io/GraphvizOnline/](https://dreampuf.github.io/GraphvizOnline/)

---

## 🧩 Estado actual del compilador

| Etapa | Estado | Descripción |
|--------|---------|-------------|
| **Análisis léxico** | ✅ Implementado | Reconoce identificadores, literales, operadores, palabras clave y símbolos. |
| **Análisis sintáctico** | ✅ Implementado | Reconoce estructuras de control (`for`, `if`, `print`, etc.), declaraciones y expresiones. |
| **AST** | ✅ Implementado | Genera una representación jerárquica del programa. |
| **Visualización gráfica del AST** | ✅ Implementado | Exporta el árbol a `.dot` y `.pdf`. |
| **Tokens no usados** | ⚠️ Pendiente | Falta integrar `DO`, `WHILE`, `AUTO` en la gramática. |
| **Análisis semántico** | 🚧 En desarrollo | Validación de tipos, alcance de variables, etc. |
| **Generación de código intermedio o máquina** | ⏳ No implementado | Próxima fase del compilador. |

---

## 🧰 Requisitos del entorno

- **Python 3.10+**
- **Librería SLY**
  ```bash
  pip install sly
  ```
- **Graphviz** (para generar y visualizar los archivos `.dot`)
  ```bash
  sudo apt install graphviz
  # o en Windows: descargar desde graphviz.org
  ```

---

## 🧪 Ejemplo de flujo completo

```bash
# 1. Escanear el archivo fuente
python bminor.py --scan test/sieve.bminor

# 2. Analizar la estructura sintáctica
python bminor.py --parse test/sieve.bminor

# 3. Generar y visualizar el AST
python astprint.py test/sieve.bminor
```

Archivos generados:
```
dot/
├── sieve.dot
└── sieve.pdf
```
