# 📖 Analizador Léxico en Python con SLY  

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
