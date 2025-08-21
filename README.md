# 📖 Analizador Léxico en Python con SLY  

### Universidad Tecnológica de Pereira
### Facultad de Ingenierías
### Departamento de Ingeniería de Sistemas y Computación

### Docente
Angel Augusto Agudelo Zapata

### Estudiantes

**Nombres:**
- Andrés Felipe Mogollón España   
- Felipe Borja   
- Juan Darío Malagon  

**Fecha:** 19/08/2025  


### Ingeniería de Sistemas y Computación – Jornada Especial
## Introducción

Este proyecto implementa un **analizador léxico (lexer)** en **Python** utilizando la librería [SLY (Sly Lex-Yacc)](https://github.com/dabeaz/sly), una herramienta moderna para la construcción de analizadores léxicos y sintácticos.  

El analizador se encarga de **leer un código fuente** y **dividirlo en tokens**, que son las unidades básicas del lenguaje (palabras reservadas, identificadores, operadores, literales, etc.). Estos tokens luego pueden ser utilizados en la etapa de **análisis sintáctico** para construir un compilador o intérprete.  

## ✨ Características
- Implementado en **Python 3**.  
- Uso de **SLY** para la definición de reglas léxicas.  
- Reconocimiento de:  
  - Palabras reservadas.  
  - Identificadores.  
  - Operadores aritméticos y lógicos.  
  - Números enteros y flotantes.  
  - Símbolos especiales.  
- Manejo básico de errores léxicos.  

## 🚀 Ejecución
1. Clonar el repositorio:  
   ```bash
   git clone https://github.com/Keiro18/Lexer.git
   cd Lexer



## 📑 Resumen  
Este proyecto implementa un **analizador léxico (lexer)** en **Python** utilizando la librería [SLY (Sly Lex-Yacc)](https://github.com/dabeaz/sly).  
El analizador convierte un código fuente en una secuencia de **tokens**, que luego podrán ser usados por un analizador sintáctico en un compilador o intérprete.  

Se implementaron:  
- Palabras reservadas.  
- Identificadores.  
- Operadores aritméticos, lógicos y de comparación.  
- Literales enteros, flotantes, caracteres y cadenas.  
- Comentarios estilo **C** (`/* */`) y **C++** (`//`).  
- Manejo de errores básicos para caracteres no reconocidos.  

---

## 📝 Tabla de Tokens  

| **Token**        | **Expresión Regular** | **Ejemplo Válido** | **Ejemplo Inválido** |
|------------------|------------------------|---------------------|----------------------|
| ID               | `[_a-zA-Z]\w*`        | `var1`, `nombre`   | `1abc`, `@id`        |
| INT_LITERAL      | `[+-]?\d+`            | `42`, `-7`         | `12a`, `++3`         |
| FLOAT_LITERAL    | `([+-]?(\d+\.\d*|\.\d+)([eE][+-]?\d+)?|\d+[eE][+-]?\d+)` | `3.14`, `2e10` | `1.2.3`, `e10` |
| CHAR_LITERAL     | `'(...caracter...)'`   | `'a'`, `'\n'`     | `'ab'`, `''`         |
| STRING_LITERAL   | `"( ... )*"`           | `"hola"`, `"\t"`  | `"unterminated`      |
| Operadores       | `+ - * / % ^ == != <= >= < > && || ++ -- !` | `a+b`, `x&&y` | `a===b`, `x&y` |  
| Palabras clave   | `if, while, for, else, return...` | `if`, `while` | `iff`, `whiles` |  

---

## ⚠️ Manejo de Errores  
- Si se encuentra un **carácter no válido**, el lexer muestra un mensaje de error con el número de línea:  
  ```
  Line 3: Bad character '@'
  ```  
- Los errores no detienen el análisis de todo el archivo; simplemente **se ignoran los caracteres inválidos** y se continúa.  

---

## 🔍 Casos de Prueba  
Se diseñaron dos conjuntos de pruebas:  

1. **Pruebas válidas (`test/scanner/good*.bminor`)**  
   - Contienen identificadores, números, strings y operadores correctamente escritos.  
   - Verifican que los tokens se imprimen de forma correcta.  

2. **Pruebas inválidas (`test/scanner/bad*.bminor`)**  
   - Incluyen literales mal formados, identificadores incorrectos y cadenas sin cerrar.  
   - Verifican que el lexer arroje mensajes de error y termine con código de salida `1`.  

3. **Validación contra ejemplos (`test/validationAgainstExamples/`)**  
   - Incluyen operadores, formatos de `float`, escapes en caracteres y strings, identificadores límite, y comentarios de tipo C/C++.  

---

## 💻 Ejecución de Pruebas  
Los casos se prueban manualmente con el comando:  

```bash
python sieve.bminor --scan archivo.bminor
```  

Ejemplo de ejecución:  

```
>>> python bminor.py --scan test/scanner/good0.bminor
Token(type='ID', value='x', lineno=1, index=0)
Token(type='EQ', value='==', lineno=1, index=2)
Token(type='INT_LITERAL', value='10', lineno=1, index=4)
```  

---

## ✅ Conclusión  
El analizador léxico cumple con los objetivos planteados: reconocer palabras reservadas, operadores, literales e identificadores del lenguaje **B-Minor**.  
Los casos de prueba muestran que funciona correctamente en entradas válidas y que detecta adecuadamente errores en entradas inválidas.  
